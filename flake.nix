{
    description = "mutli-use flake for devshell and building the application";

    inputs = {
        determinate.url = "https://flakehub.com/f/DeterminateSystems/determinate/0.1";
        nixpkgs.url = "https://flakehub.com/f/NixOS/nixpkgs/0.2511.0";
        flake-utils.url = "github:numtide/flake-utils";
        nixos-generators = {
            url = "github:nix-community/nixos-generators";
            inputs.nixpkgs.follows = "nixpkgs";
        };
        pyproject-nix = {
            url = "github:pyproject-nix/pyproject.nix";
            inputs.nixpkgs.follows = "nixpkgs";
        };
        uv2nix = {
            url = "github:pyproject-nix/uv2nix";
            inputs.pyproject-nix.follows = "pyproject-nix";
            inputs.nixpkgs.follows = "nixpkgs";
        };
        pyproject-build-systems = {
            url = "github:pyproject-nix/build-system-pkgs";
            inputs.pyproject-nix.follows = "pyproject-nix";
            inputs.uv2nix.follows = "uv2nix";
            inputs.nixpkgs.follows = "nixpkgs";
        };
    };

    outputs = { self, nixpkgs, flake-utils, determinate, nixos-generators, pyproject-nix, uv2nix, pyproject-build-systems, ... }:
        flake-utils.lib.eachDefaultSystem (system:
            let
                pkgs = import nixpkgs {
                    inherit system;
                };

                # uv2nix workspace
                workspace = uv2nix.lib.workspace.loadWorkspace { workspaceRoot = ./.; };

                # Create package overlay from workspace
                overlay = workspace.mkPyprojectOverlay {
                    sourcePreference = "wheel";
                };

                # Base Python package set from pyproject.nix
                python = pkgs.python313;
                pythonSet = (pkgs.callPackage pyproject-nix.build.packages {
                    inherit python;
                }).overrideScope (
                    pkgs.lib.composeManyExtensions [
                        pyproject-build-systems.overlays.default
                        overlay
                        # Override for packages with missing build dependencies
                        (final: prev: {
                            wsgi-request-logger = prev.wsgi-request-logger.overrideAttrs (old: {
                                nativeBuildInputs = (old.nativeBuildInputs or []) ++ [
                                    final.setuptools
                                ];
                            });
                        })
                    ]
                );

                # Create the virtual environment with all dependencies
                python_env = pythonSet.mkVirtualEnv "libu-env" workspace.deps.default;


                nodes = [
                    "libu"
                ];
                formats = [
                    "docker"
                    "proxmox"
                    "iso"
                    "install-iso"
                    "linode"
                    "amazon"
                ];

                configuration = (
                    # Function that templates out a value for the `nixosConfigurations` attrset.
                    # Used for bundling a nixos configuration for the node to be used for autoUpgrades after deployment.
                    nodename: format:
                    nixos-generators.nixosGenerate {
                        system = "x86_64-linux";
                        format = format;
                        modules = [
                            determinate.nixosModules.default
                            ./nixos-config.nix
                        ];
                        specialArgs = {
                            # additional arguments to pass to modules
                            self = self;
                            nixpkgs = nixpkgs;
                            nodename = nodename;
                            format = format;
                            inherit python_env;
                        };
                    }
                );
                generators = (
                    # Function that templates out a value for the `nixosConfigurations` attrset.
                    # Used for bundling a nixos configuration for the node to be used for autoUpgrades after deployment.
                    nodename: format:
                    nixpkgs.lib.nixosSystem {
                        system = "x86_64-linux";
                        format = format;
                        modules = [
                            determinate.nixosModules.default
                            ./nixos-config.nix
                        ];
                        specialArgs = {
                            # additional arguments to pass to modules
                            self = self;
                            nixpkgs = nixpkgs;
                            nodename = nodename;
                            format = format;
                            inherit python_env;
                        };
                    }
                );

            in {
                # Export python_env so it can be used in nixos-config.nix
                inherit python_env;

                devShells.default = pkgs.mkShell {
                    name = "libu-dev-shell";

                    packages = [
                        python_env
                        pkgs.uv
                        pkgs.awscli2
                    ];
                };

                # This evaluates to something like: {"libu-amazon" = nixpkgs.lib.nixosGenerate {...}; ... }
                packages = builtins.listToAttrs (
                    builtins.concatMap ( format:
                        map
                        ( nodename: { "name" = "${nodename}-${format}"; "value" = configuration nodename format; } )
                        nodes  # List of nodes to generate images for
                    )
                    formats
                );
                nixosConfigurations = builtins.listToAttrs (
                    builtins.concatMap ( format:
                        ( nodename: { "name" = "${nodename}"; "value" = generators nodename format; } )
                        nodes  # List of nodes to generate nixos configs for
                    )
                    formats
                );
            });
}
