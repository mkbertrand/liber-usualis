{
    description = "mutli-use flake for devshell and building the application";

    inputs = {
        determinate.url = "https://flakehub.com/f/DeterminateSystems/determinate/0.1";
        nixpkgs.url = "https://flakehub.com/f/NixOS/nixpkgs/0.2411.0";
        flake-utils.url = "github:numtide/flake-utils";
        nixos-generators = {
            url = "github:nix-community/nixos-generators";
            inputs.nixpkgs.follows = "nixpkgs";
        };
    };

    outputs = { self, nixpkgs, flake-utils, determinate, nixos-generators,... }:
        flake-utils.lib.eachDefaultSystem (system:
            let
                pkgs = import nixpkgs {
                    inherit system;
                };

                python_env = pkgs.python3.withPackages (ps: with ps; [
                    bottle
                    pytest
                    diff-match-patch
                    requests
                    black
                ]);

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
                            python_env = python_env;
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
                            python_env = python_env;
                        };
                    }
                );

            in {
                devShells.default = pkgs.mkShell {
                    name = "libu-dev-shell";

                    packages = [
                        python_env
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
