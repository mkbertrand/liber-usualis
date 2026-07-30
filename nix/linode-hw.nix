{
  lib,
  config,
  pkgs,
  modulesPath,
  ...
}:
{

  # # Linode uses GRUB2 and a standard disk layout
  # fileSystems."/" = lib.mkDefault {
  #   device = "/dev/sda";
  #   fsType = "ext4";
  # };

  boot.loader.grub = lib.mkDefault {
    enable = true;
    device = "nodev";
  };

  # Linode uses DHCP
  networking.useDHCP = lib.mkDefault true;

  imports = [
    (modulesPath + "/profiles/qemu-guest.nix")
  ];

  boot.initrd.availableKernelModules = [
    "virtio_pci"
    "virtio_scsi"
    "ahci"
    "sd_mod"
  ];
  boot.initrd.kernelModules = [ ];
  boot.kernelModules = [ ];
  boot.extraModulePackages = [ ];

  fileSystems."/" = {
    device = "/dev/disk/by-uuid/f222513b-ded1-49fa-b591-20ce86a2fe7f";
    fsType = "ext4";
  };

  swapDevices = [
    { device = "/dev/disk/by-uuid/f1408ea6-59a0-11ed-bc9d-525400000001"; }
  ];

  nixpkgs.hostPlatform = lib.mkDefault "x86_64-linux";

}
