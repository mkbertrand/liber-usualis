{ lib, nixpkgs, format, nodename, python_env, ... }:
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
        src = ./.;
        buildInputs = [
            app_pkgs
        ];
        buildPhase = ''
            mkdir -p $out/lib
            cp -r . $out/lib/
            '';
    };
in
    {
    config = {

        # set ntp
        services.chrony.enable = lib.mkDefault true;
        time.timeZone = lib.mkDefault "America/Chicago";

        networking = {
            hostName = "nixos-${nodename}-${format}";
            firewall = {
                enable = true;
                allowedTCPPorts = [ 22 80 443 ];
            };

        };

        users.users.master = lib.mkDefault {
            isNormalUser = true;
            extraGroups = [ "wheel" ]; # Enable ‘sudo’ for the user.
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
                "ADD YOUR PUBKEY HERE"
            ];
        };
        users.groups.master = {};

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
            python_env
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

                #                 "liberusualis.org" = {
                #                     # Main server with SSL
                #                     enableACME = true;  # Use Let's Encrypt
                #                     forceSSL = true;    # Redirect HTTP to HTTPS
                #
                #                     # Proxy to bottle application
                #                     locations."/".proxyPass = "http://127.0.0.1:8080";
                #
                #                     # If you need to include additional proxy parameters
                #                     locations."/".extraConfig = ''
                # # This replaces the include proxy_params;
                # proxy_set_header Host $host;
                # proxy_set_header X-Real-IP $remote_addr;
                # proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                # proxy_set_header X-Forwarded-Proto $scheme;
                #                     '';
                #                 };

                # # Redirect www to non-www
                # "www.liberusualis.org" = {
                #     enableACME = true;  # Use Let's Encrypt
                #     forceSSL = true;    # Redirect HTTP to HTTPS
                #     globalRedirect = "liberusualis.org";
                # };

                "ec2-3-144-118-245.us-east-2.compute.amazonaws.com" = {
                    # Main server with SSL
                    enableACME = true;  # Use Let's Encrypt
                    forceSSL = true;    # Redirect HTTP to HTTPS

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
                "www.ec2-3-144-118-245.us-east-2.compute.amazonaws.com" = {
                    enableACME = true;  # Use Let's Encrypt
                    forceSSL = true;    # Redirect HTTP to HTTPS
                    globalRedirect = "ec2-3-144-118-245.us-east-2.compute.amazonaws.com";
                };

            };
        };

        # Let's Encrypt configuration
        security.acme = {
            acceptTerms = true;
            defaults.email = "mkbertrand@gmail.com";  # Replace with your email
        };

        systemd.services = {
            bottle_app = {
                description = "Bottle Application";
                wantedBy = [ "multi-user.target" ];
                serviceConfig = {
                    ExecStart = "${python_env}/bin/python ${bottle_app.out}/lib/frontend.py";
                    Restart = "always";
                    User = "bottle";
                    Group = "bottle";
                    WorkingDirectory = "${bottle_app.out}/lib";
                    Environment = [
                        "out=${bottle_app.out}"
                        "PATH=${lib.makeBinPath app_pkgs}:$PATH"
                        "PYTHONPATH=${bottle_app}/lib/bottle_app:$PYTHONPATH"
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
        users.groups.bottle = {};

    } // lib.optionalAttrs (format == "proxmox") {
            proxmox = lib.mkDefault {
                qemuConf = {
                    bios = "seabios";
                    virtio0 = "local-zfs:vm-102-disk-0"; # WARN: replace with whatever storage you have set up
                    name = "nixos-${nodename}-${format}";
                };
                cloudInit.defaultStorage = "local-zfs"; # WARN: replace with whatever storage you have set up
            };
            networking = {
                defaultGateway = "192.168.0.1";
                nameservers = [ "8.8.8.8" "8.8.4.4" ];  # Google's public DNS servers, or replace with your own
                useDHCP = false;
                interfaces.ens18.ipv4.addresses = [ { address = "192.168.0.36"; prefixLength = 24; } ];
                hostName = "nixos-${nodename}-${format}";
                firewall = {
                    enable = true;
                    allowedTCPPorts = [ 22 80 443 ];
                };
            };
        } // lib.optionalAttrs (format == "amazon") {
            virtualisation.diskSize = 4 * 1024;
            boot.loader.grub = {
                enable = true;
                device = "/dev/xvda"; # Common for AWS instances
            };
        } ;
}

