{
  lib,
  nixpkgs,
  format ? null,
  nodename,
  python_env,
  frontend_assets,
  chant,
  fcc,
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

  bottle_app = pkgs.stdenv.mkDerivation {
    name = "bottle_app";
    src = self;
    buildInputs = app_pkgs;
    buildPhase = ''
      mkdir -p $out/lib
      cp -r . $out/lib/
      mkdir -p $out/lib/web/resources/dist
      cp -r ${frontend_assets}/. $out/lib/web/resources/dist/
    '';
  };
  domain = "liberusualis.org";
in
{
  config = {

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
        "bottle"
      ]; # Enable 'sudo' for the user, bottle for shared /var/lib/libu access
      packages = with pkgs; [
        curl
        git
        neovim
        tree
        wget
      ];
      initialHashedPassword = "$6$YRItpShEzQ4/hiUt$cYKAIWY906xWz2ZqbgSq6F070it0NOPfqGF.sbEuSMtiVdMpx43i4RelYeQP/DfIgAy/G/7isuCgGnmdH09QB1";
      openssh.authorizedKeys.keys = [
        "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIHANoftEQ3KqBK2UegRTWFVmLyJSYqzYAhbLgIqrtS7T master@vm-nixos-mywebsite"
        "ecdsa-sha2-nistp521 AAAAE2VjZHNhLXNoYTItbmlzdHA1MjEAAAAIbmlzdHA1MjEAAACFBAG8NzNAYDdt66g3YlH9/JpemTq87v5auOVQMJ128U78Kwyc9Dq8vYELxpglHWg4ILwmNp8mgAC9tDnmNI24PY1RgQG7Mq2cIciPPf8B8ebR3v0nMi5KHRR5cCf7FXpPqbPMAuqzz748gnCkpGypdquz2Psywxe02b/jwLDNrhoKORmJiA== vir@nixos"
        "ADD YOUR PUBKEY HERE"
      ];
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
        #                     # Proxy to bottle application
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

          # Proxy to bottle application
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
        #   # Proxy to bottle application
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
      defaults.email = "mkbertrand@gmail.com"; # Replace with your email
    };

    systemd.services = {
      bottle_app_setup = {
        description = "Copy Bottle Application to /var/lib/libu";
        wantedBy = [ "multi-user.target" ];
        before = [ "bottle_app.service" ];
        serviceConfig = {
          Type = "oneshot";
          RemainAfterExit = true;
          ExecStart = pkgs.writeShellScript "bottle-app-setup" ''
            set -euo pipefail
            ${pkgs.rsync}/bin/rsync -a --delete --exclude=/books.json --exclude=/data/generated/ ${bottle_app.out}/lib/ /var/lib/libu/
            ${pkgs.coreutils}/bin/mkdir -p /var/lib/libu/data/generated/liber-usualis-chant /var/lib/libu/data/generated/fcc
            ${pkgs.rsync}/bin/rsync -a --delete ${chant}/ /var/lib/libu/data/generated/liber-usualis-chant/
            ${pkgs.rsync}/bin/rsync -a --delete ${fcc}/ /var/lib/libu/data/generated/fcc/
          '';
          User = "root";
          Group = "root";
        };
        # Fix permissions after copy
        postStart = ''
          ${pkgs.coreutils}/bin/chown -R bottle:bottle /var/lib/libu
          ${pkgs.coreutils}/bin/chmod -R 0775 /var/lib/libu
        '';
      };
      bottle_app = {
        description = "Bottle Application";
        wantedBy = [ "multi-user.target" ];
        after = [ "bottle_app_setup.service" ];
        requires = [ "bottle_app_setup.service" ];
        serviceConfig = {
          ExecStart = "${python_env}/bin/python /var/lib/libu/server.py";
          Restart = "always";
          User = "bottle";
          Group = "bottle";
          WorkingDirectory = "/var/lib/libu";
          Environment = [
            "PATH=${lib.makeBinPath app_pkgs}:$PATH"
            "PYTHONPATH=/var/lib/libu:$PYTHONPATH"
            "LOG_PATH=/var/lib/libu/log.log"
          ];
        };
      };
    };

    # Create user and group for the service
    users.users.bottle = {
      isSystemUser = true;
      group = "bottle";
      createHome = true;
    };
    users.groups.bottle = { };

    # Create /var/lib/libu with proper permissions for bottle and master
    systemd.tmpfiles.rules = [
      "d /var/lib/libu 0775 bottle bottle -"
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
