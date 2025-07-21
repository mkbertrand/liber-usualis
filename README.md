# Liber Usualis Project

A project dedicated to making the Mass, Hours, and Rites of various editions of the Roman Rite easily accessible and beautifully formatted with or without their chants.

## Program Design

The Liber Usualis codebase is primarily data-driven, with very few hard-coded elements, opting instead to have a tag-lookup system for constructing Rites.

## Usage

### Installation

```bash
git clone https://github.com/mkbertrand/liber-usualis
git clone https://github.com/mkbertrand/franciscan-chant-closet
cd liber-usualis
pip install bottle pytest diff-match-patch waitress wsgi-request-logger
```

Note: diff-match-patch is only necessary for test_breviarium.
### Running

To run the server (by default on localhost:8080, frontend.py is run as follows:

```bash
./frontend.py
```
Note: for full functionality, franciscan-chant-closet must be run at the same time and must be able to bind to port 40081.
## Author

Miles Bertrand

## Contributors

Albert-Emanuel Milani

Jacob Heilman

## Additional Credit

Benjamin Bloomfield (whose Javascript code I 'borrowed' and whose Compline project initially inspired this project)

## License

All files within this project are released under the GNU Affero General Public License (AGPL-3.0 or later) unless otherwise indicated in the file.


# deploying
## deploy image to proxmox
```bash
export PROXMOX_HOST_IP="192.168.0.11"; # use the IP of one of your proxmox hosts
export VM_ID="107"; # use whatever VM_ID is not already in use
export IMAGE_PATH="$(realpath result/* | tail -n1)";
scp $IMAGE_PATH root@$PROXMOX_HOST_IP:/var/lib/vz/dump/ && \
ssh root@$PROXMOX_HOST_IP "if pvesh get /nodes/\$(hostname -s)/qemu/$VM_ID --noborder 2>/dev/null; then \
  echo 'VM $VM_ID exists, deleting...' && \
  qm stop $VM_ID && \
  qm destroy $VM_ID --purge; \
fi && \
qmrestore /var/lib/vz/dump/$(basename $IMAGE_PATH) $VM_ID --unique true && \
qm start $VM_ID"
```
## deploy image to aws ec2
not tested yet [see this](https://github.com/nix-community/nixos-generators/issues/343)
```bash
nix build .#libu-amazon;
export IMAGE_PATH="$(realpath result/* | head -n1)";
aws configure; # setup your aws auth if it's not already configured
aws s3 mb s3://nixos-iam-bucket; # create the nixos iam bucket in s3
aws s3 cp "$IMAGE_PATH" s3://nixos-iam-bucket; # copy the result of nixos-generators nix build to the s3 bucket
aws s3api put-bucket-policy --bucket nixos-iam-bucket --policy file://bucket-policy.json; # add the bucket policy
aws iam create-role --role-name vmimport --assume-role-policy-document file://vmimport-trust-policy.json # First create the role with the trust policy
aws iam put-role-policy --role-name vmimport --policy-name vmimport-policy --policy-document file://vmimport-policy.json # Then attach the permission policy (not the trust policy)
aws ec2 import-snapshot --description "Imported nixos VHD" --disk-container file://containers.json | cat; # import the image as an iam
aws ec2 describe-import-image-tasks --import-task-ids import-snap-4621525fac5e4474t | cat; # monitor the import progress with this, using the task id from the previous command
aws ec2 register-image \
    --name "nixos-libu" \
    --architecture "x86_64" \
    --boot-mode "legacy-bios" \
    --root-device-name '/dev/xvda' \
    --virtualization-type hvm \
    --ena-support \
    --imds-support='v2.0' \
    --sriov-net-support simple \
    --block-device-mappings "file://block-mapping.json"

```
the import-image command might take 30ish minutes to run, so there's probably a better way of creating the new IAM, maybe even just having the nixos config as a public or private flake and running nixos-rebuild switch on the ec2 instance machine with the flake as the target
