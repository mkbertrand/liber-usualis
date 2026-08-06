{
  description = "mutli-use flake for devshell and building the application";

  inputs = {
    chant = {
      url = "github:mkbertrand/liber-usualis-chant/master";
      flake = false;
    };
    determinate.url = "https://flakehub.com/f/DeterminateSystems/determinate/0.1";
    fcc = {
      url = "github:mkbertrand/franciscan-chant-closet/databased";
      flake = false;
    };
    nixpkgs.url = "https://flakehub.com/f/NixOS/nixpkgs/0.2605.0";
    flake-utils.url = "github:numtide/flake-utils";
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
      chant,
      fcc,
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

      imageConfiguration = nixpkgs.lib.nixosSystem {
        system = nixosSystem;
        modules = [
          determinate.nixosModules.default
          ./nix/nixos-config.nix
          ./nix/image-formats.nix
        ];
        specialArgs = {
          inherit self nixpkgs python_env;
          nodename = "libu";
          format = null;
        };
      };

      imagePackages = {
        libu-proxmox = imageConfiguration.config.system.build.images.proxmox;
        libu-iso = imageConfiguration.config.system.build.images.iso;
        libu-install-iso = imageConfiguration.config.system.build.images.iso-installer;
        libu-linode = imageConfiguration.config.system.build.images.linode;
        libu-amazon = imageConfiguration.config.system.build.images.amazon;
      };

      linodeConfiguration = nixpkgs.lib.nixosSystem {
        system = nixosSystem;
        modules = [
          determinate.nixosModules.default
          ./nix/nixos-config.nix
          ./nix/linode-hw.nix
        ];
        specialArgs = {
          inherit self nixpkgs python_env;
          nodename = "libu";
          format = "linode";
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
            pkgs.jq
          ];
          shellHook = ''
            mkdir -p "$PWD/data/generated/liber-usualis-chant" "$PWD/data/generated/fcc"
            chmod -R u+w "$PWD/data/generated/liber-usualis-chant" "$PWD/data/generated/fcc"
            ${pkgs.coreutils}/bin/cp -Rsf ${chant}/. "$PWD/data/generated/liber-usualis-chant/"
            ${pkgs.coreutils}/bin/cp -Rsf ${fcc}/. "$PWD/data/generated/fcc/"
          '';
        };

        packages = nixpkgs.lib.optionalAttrs (system == nixosSystem) imagePackages;
      }
    )
    // {
      nixosConfigurations = {
        libu-images = imageConfiguration;
        libu-linode = linodeConfiguration;
      };
    };
}
