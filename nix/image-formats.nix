{
  lib,
  nodename,
  ...
}:
let
  imageHostName = format: "nixos-${nodename}-${format}";
in
{
  fileSystems."/" = {
    device = lib.mkOverride 1400 "/dev/disk/by-label/nixos";
    fsType = lib.mkOverride 2000 "ext4";
  };
  boot.loader.grub.devices = lib.mkDefault [ "nodev" ];

  image.modules = {
    proxmox = {
      networking = {
        hostName = imageHostName "proxmox";
        defaultGateway = "192.168.0.1";
        nameservers = [
          "8.8.8.8"
          "8.8.4.4"
        ];
        useDHCP = false;
        interfaces.ens18.ipv4.addresses = [
          {
            address = "192.168.0.36";
            prefixLength = 24;
          }
        ];
      };

      proxmox = {
        qemuConf = {
          bios = "seabios";
          virtio0 = "local-zfs:vm-102-disk-0";
          name = imageHostName "proxmox";
        };
        cloudInit.defaultStorage = "local-zfs";
      };
    };

    iso = {
      networking.hostName = imageHostName "iso";
      isoImage = {
        makeEfiBootable = true;
        makeUsbBootable = true;
      };
    };

    iso-installer = {
      networking.hostName = imageHostName "install-iso";
      systemd.services = {
        wpa_supplicant.wantedBy = lib.mkForce [ "multi-user.target" ];
        sshd.wantedBy = lib.mkForce [ "multi-user.target" ];
      };
    };

    linode.networking.hostName = imageHostName "linode";

    amazon = {
      networking.hostName = imageHostName "amazon";
      virtualisation.diskSize = 4 * 1024;
      fileSystems."/".autoResize = true;
    };
  };
}
