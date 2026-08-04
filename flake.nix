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

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      determinate,
      nixos-generators,
      pyproject-nix,
      uv2nix,
      pyproject-build-systems,
      ...
    }:
    let
      # Helper function to create python_env for a given system
      mkPythonEnv =
        system:
        let
          pkgs = import nixpkgs { inherit system; };
          workspace = uv2nix.lib.workspace.loadWorkspace { workspaceRoot = ./.; };
          overlay = workspace.mkPyprojectOverlay { sourcePreference = "wheel"; };
          python = pkgs.python313;
          pythonSet =
            (pkgs.callPackage pyproject-nix.build.packages {
              inherit python;
            }).overrideScope
              (
                pkgs.lib.composeManyExtensions [
                  pyproject-build-systems.overlays.default
                  overlay
                  (final: prev: {
                    wsgi-request-logger = prev.wsgi-request-logger.overrideAttrs (old: {
                      nativeBuildInputs = (old.nativeBuildInputs or [ ]) ++ [
                        final.setuptools
                      ];
                    });
                  })
                ]
              );
        in
        pythonSet.mkVirtualEnv "libu-env" workspace.deps.default;

      # NixOS configuration helpers (always x86_64-linux)
      nixosSystem = "x86_64-linux";
      python_env = mkPythonEnv nixosSystem;

      nodes = [ "libu" ];
      formats = [
        "docker"
        "proxmox"
        "iso"
        "install-iso"
        "linode"
        "amazon"
      ];

      # For nixos-generators packages
      configuration =
        nodename: format:
        nixos-generators.nixosGenerate {
          system = nixosSystem;
          inherit format;
          modules = [
            determinate.nixosModules.default
            ./nix/nixos-config.nix
          ];
          specialArgs = {
            inherit
              self
              nixpkgs
              nodename
              format
              python_env
              ;
          };
        };

      # For nixosConfigurations (nixos-rebuild)
      generators =
        nodename: format: hardwareModule:
        nixpkgs.lib.nixosSystem {
          system = nixosSystem;
          modules = [
            determinate.nixosModules.default
            ./nix/nixos-config.nix
            hardwareModule
          ];
          specialArgs = {
            inherit
              self
              nixpkgs
              nodename
              format
              python_env
              ;
          };
        };

    in
    # Merge per-system outputs with top-level nixosConfigurations
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs { inherit system; };
        systemPythonEnv = mkPythonEnv system;
      in
      {
        python_env = systemPythonEnv;

        devShells.default = pkgs.mkShell {
          name = "libu-dev-shell";
          packages = [
            systemPythonEnv
            pkgs.uv
            pkgs.awscli2
          ];
        };

        # Image packages (nixos-generators)
        packages = builtins.listToAttrs (
          builtins.concatMap (
            format:
            map (nodename: {
              name = "${nodename}-${format}";
              value = configuration nodename format;
            }) nodes
          ) formats
        );
      }
    )
    // {
      # Top-level configuration for the supported nixos-rebuild target.
      nixosConfigurations.libu-linode = generators "libu" "linode" ./nix/linode-hw.nix;
    };
}
