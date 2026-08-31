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

      mkFrontendAssets =
        system:
        let
          pkgs = import nixpkgs { inherit system; };
        in
        pkgs.buildNpmPackage {
          pname = "liber-usualis-frontend";
          version = "1.0.0";
          src = self;

          npmDeps = pkgs.importNpmLock {
            npmRoot = self;
            packageSourceOverrides."node_modules/exsurge" = pkgs.fetchFromGitHub {
              owner = "bbloomf";
              repo = "exsurge";
              rev = "v1.26.1";
              hash = "sha256-9dwIZvmhu2RmNQ0KXMhw/dWegkOiYwdl5tmvoI2fVpE=";
            };
          };
          npmConfigHook = pkgs.importNpmLock.npmConfigHook;
          npmBuildScript = "build";

          installPhase = ''
            runHook preInstall
            mkdir -p "$out"
            cp -r web/resources/dist/. "$out/"
            runHook postInstall
          '';
        };

      # NixOS configuration helpers (always x86_64-linux)
      nixosSystem = "x86_64-linux";
      python_env = mkPythonEnv nixosSystem;
      frontend_assets = mkFrontendAssets nixosSystem;

      imageConfiguration = nixpkgs.lib.nixosSystem {
        system = nixosSystem;
        modules = [
          determinate.nixosModules.default
          ./nix/nixos-config.nix
          ./nix/image-formats.nix
        ];
        specialArgs = {
          inherit
            self
            nixpkgs
            python_env
            frontend_assets
            chant
            fcc
            ;
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
          inherit
            self
            nixpkgs
            python_env
            frontend_assets
            chant
            fcc
            ;
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
        frontendAssets = mkFrontendAssets system;
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
            pkgs.nodejs
          ];
          shellHook = ''
            mkdir -p "$PWD/data/generated/liber-usualis-chant" "$PWD/data/generated/fcc"
            mkdir -p "$PWD/web/resources/dist"
            chmod -R u+w "$PWD/data/generated/liber-usualis-chant" "$PWD/data/generated/fcc"
            ${pkgs.coreutils}/bin/cp -Rsf ${chant}/. "$PWD/data/generated/liber-usualis-chant/"
            ${pkgs.coreutils}/bin/cp -Rsf ${fcc}/. "$PWD/data/generated/fcc/"
            ${pkgs.coreutils}/bin/rm -f "$PWD/web/resources/dist"/{pray.js,pray.js.map,pray.css,pray.css.map}
            ${pkgs.coreutils}/bin/cp ${frontendAssets}/* "$PWD/web/resources/dist/"
            ${pkgs.coreutils}/bin/chmod u+w "$PWD/web/resources/dist"/*
          '';
        };

        packages = {
          frontend-assets = frontendAssets;
        }
        // nixpkgs.lib.optionalAttrs (system == nixosSystem) imagePackages;
      }
    )
    // {
      nixosConfigurations = {
        libu-images = imageConfiguration;
        libu-linode = linodeConfiguration;
      };
    };
}
