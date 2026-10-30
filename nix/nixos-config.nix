{
  config,
  lib,
  nixpkgs,
  format ? null,
  nodename,
  python_env,
  frontend_assets,
  self,
  ...
}:
let
  system = "x86_64-linux";
  pkgs = nixpkgs.legacyPackages.${system};

  # App packages
  app_pkgs = with pkgs; [
    python_env
    # whatever else you want to add here
    btop
  ];

  libu_app = pkgs.stdenv.mkDerivation {
    name = "libu";
    src = self;
    buildInputs = app_pkgs;
    buildPhase = ''
      mkdir -p $out/lib
      cp -r . $out/lib/
      mkdir -p $out/lib/web/resources/dist
      cp -r ${frontend_assets}/. $out/lib/web/resources/dist/
    '';
  };
  domain = config.libu.domain;
in
{
  options.libu.domain = lib.mkOption {
    type = lib.types.str;
    default = "liberusualis.org";
    description = "Domain served by nginx; www.<domain> redirects to it.";
  };

  # No default: each deployment's private flake supplies the keys allowed to log in as master
  options.libu.authorizedKeys = lib.mkOption {
    type = lib.types.listOf lib.types.str;
    description = "SSH public keys authorized for the master user.";
  };

  config = {

    assertions = [
      {
        assertion = config.libu.authorizedKeys != [ ];
        message = "libu.authorizedKeys must list at least one SSH public key.";
      }
    ];

    # set ntp
    services.chrony.enable = lib.mkDefault true;
    time.timeZone = lib.mkDefault "America/Chicago";
    system.stateVersion = "26.05";

    networking = {
      hostName = lib.mkDefault ("nixos-${nodename}" + lib.optionalString (format != null) "-${format}");
      firewall = {
        enable = true;
        allowedTCPPorts = [
          22
          80
          443
        ];
      };

    };

    users.users.master = lib.mkDefault {
      isNormalUser = true;
      extraGroups = [
        "wheel"
        "libu"
      ]; # Enable 'sudo' for the user, libu for shared /var/lib/libu access
      packages = with pkgs; [
        curl
        git
        neovim
        tree
        wget
      ];
      initialHashedPassword = "$6$YRItpShEzQ4/hiUt$cYKAIWY906xWz2ZqbgSq6F070it0NOPfqGF.sbEuSMtiVdMpx43i4RelYeQP/DfIgAy/G/7isuCgGnmdH09QB1";
      openssh.authorizedKeys.keys = config.libu.authorizedKeys;
    };
    users.groups.master = { };

    security.sudo = {
      enable = true;
      wheelNeedsPassword = false;
    };

    # Enable the OpenSSH daemon.
    services.openssh.enable = true;

    environment.systemPackages = with pkgs; [
      neovim
      wget
      curl
      git
      file
    ];

    services.nginx = {
      enable = true;

      # Recommended: Global settings if needed
      # recommendedGzipSettings = true;
      # recommendedOptimisation = true;
      # recommendedProxySettings = true;
      # recommendedTlsSettings = true;

      virtualHosts = {

        #                 # this is the catch-all host for local testing
        #                 "_" = {
        #                     # Proxy to the application
        #                     locations."/".proxyPass = "http://127.0.0.1:8080";
        #                     # If you need to include additional proxy parameters
        #                     locations."/".extraConfig = ''
        # # This replaces the include proxy_params;
        # proxy_set_header Host $host;
        # proxy_set_header X-Real-IP $remote_addr;
        # proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        # proxy_set_header X-Forwarded-Proto $scheme;
        #                     '';
        #                 };

        "${domain}" = {
          # Main server with SSL
          enableACME = true; # Use Let's Encrypt
          forceSSL = true; # Redirect HTTP to HTTPS

          # Proxy to the application
          locations."/".proxyPass = "http://127.0.0.1:8080";

          # If you need to include additional proxy parameters
          locations."/".extraConfig = ''
            # This replaces the include proxy_params;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
          '';
        };

        # Redirect www to non-www
        "www.${domain}" = {
          enableACME = true; # Use Let's Encrypt
          forceSSL = true; # Redirect HTTP to HTTPS
          globalRedirect = domain;
        };

        # "ec2-3-144-118-245.us-east-2.compute.amazonaws.com" = {
        #   # Main server with SSL
        #   enableACME = true; # Use Let's Encrypt
        #   forceSSL = true; # Redirect HTTP to HTTPS
        #
        #   # Proxy to the application
        #   locations."/".proxyPass = "http://127.0.0.1:8080";
        #
        #   # If you need to include additional proxy parameters
        #   locations."/".extraConfig = ''
        #     # This replaces the include proxy_params;
        #     proxy_set_header Host $host;
        #     proxy_set_header X-Real-IP $remote_addr;
        #     proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        #     proxy_set_header X-Forwarded-Proto $scheme;
        #   '';
        # };
        #
        # # Redirect www to non-www
        # "www.ec2-3-144-118-245.us-east-2.compute.amazonaws.com" = {
        #   enableACME = true; # Use Let's Encrypt
        #   forceSSL = true; # Redirect HTTP to HTTPS
        #   globalRedirect = "ec2-3-144-118-245.us-east-2.compute.amazonaws.com";
        # };

      };
    };

    # Let's Encrypt configuration
    security.acme = {
      acceptTerms = true;
      defaults.email = "mileskbertrand@liberusualis.org";
    };

    systemd.services = {
      libu-setup = {
        description = "Copy the application to /var/lib/libu";
        wantedBy = [ "multi-user.target" ];
        before = [ "libu.service" ];
        serviceConfig = {
          Type = "oneshot";
          RemainAfterExit = true;
          ExecStart = pkgs.writeShellScript "libu-setup" ''
            set -euo pipefail
            ${pkgs.rsync}/bin/rsync -a --delete ${libu_app.out}/lib/ /var/lib/libu/
          '';
          User = "root";
          Group = "root";
        };
        # Fix permissions after copy
        postStart = ''
          ${pkgs.coreutils}/bin/chown -R libu:libu /var/lib/libu
          ${pkgs.coreutils}/bin/chmod -R 0775 /var/lib/libu
        '';
      };
      libu = {
        description = "Liber Usualis server";
        wantedBy = [ "multi-user.target" ];
        after = [ "libu-setup.service" ];
        requires = [ "libu-setup.service" ];
        serviceConfig = {
          ExecStart = "${python_env}/bin/python /var/lib/libu/server.py";
          Restart = "always";
          User = "libu";
          Group = "libu";
          WorkingDirectory = "/var/lib/libu";
          Environment = [
            "PATH=${lib.makeBinPath app_pkgs}:$PATH"
            "PYTHONPATH=/var/lib/libu:$PYTHONPATH"
          ];
        };
      };
    };

    # Create user and group for the service
    users.users.libu = {
      isSystemUser = true;
      group = "libu";
      createHome = true;
    };
    users.groups.libu = { };

    # Create /var/lib/libu with proper permissions for libu and master
    systemd.tmpfiles.rules = [
      "d /var/lib/libu 0775 libu libu -"
    ];

    nix.settings = {
      trusted-users = [
        "master"
        "@wheel"
        "root"
      ];
      experimental-features = [
        "nix-command"
        "flakes"
      ];
    };

  };
}
