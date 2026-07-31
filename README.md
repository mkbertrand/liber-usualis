# Liber Usualis Project

A project dedicated to making the Mass, Hours, and Rites of various editions of the Roman Rite easily accessible and beautifully formatted with or without their chants.

## Program Design

The Liber Usualis codebase is primarily data-driven, with very few hard-coded elements, opting instead to have a tag-lookup system for constructing Rites.

[See this document for more details](./architecture.org)

## Usage

### Installation

```bash
git clone https://github.com/mkbertrand/liber-usualis
git clone https://github.com/mkbertrand/franciscan-chant-closet
cd liber-usualis
npm install github:bbloomf/exsurge
npm run build
pip install bottle pytest diff-match-patch waitress wsgi-request-logger
```

Note: diff-match-patch is only necessary for test_breviarium.
### Running

To run the server (by default on localhost:8080, the server is run as follows:

```bash
export LOG_PATH="logs.log"
python3 sync-books.py
python3 server.py
```

To run the server with output in the terminal, add the -o flag. To change the port, add the -a flag with the port.

## Author

Miles Bertrand

## Contributors

Albert-Emanuel Milani

Jacob Heilman

Volzus

David Villafana

Chandrayee

Ezekiel Warren

## Additional Credit

Benjamin Bloomfield (whose Javascript code I 'borrowed' and whose Compline project initially inspired this project)
Divinum Officium Project.
Gregobase.
Nocturnale Romanum.

## License

Each file within this project are released under the GNU Affero General Public License (AGPL-3.0 or later) unless otherwise indicated in the respective file.


# deploying
## Deploy to Linode
### Rebuild and boot an existing Linode
```bash
nix build .#libu-linode --impure;
nix-shell -p linode-cli spwgen;
export ROOT_PASS="$(spwgen uldn 16)"
echo "$ROOT_PASS"
linode-cli image-upload --label "libu-nix" --description "libu deployed to NixOS" --region "us-ord" result/nixos.img.gz;
export IMAGE_ID="$(linode-cli images list --text | awk '/libu-nix/{print $1}' | awk '{for (i=1; i<=NF; i++) last=$i} END {print last}')";
echo "imageid: $IMAGE_ID";
export LINODE_ID="$(linode-cli linodes list --text | grep "libu-nix" | cut -f1)";
export CONFIG_ID="$(linode-cli linodes configs-list $LINODE_ID | awk '/[0-9]+/{print $2}')";
echo "configid: $CONFIG_ID";
linode-cli linodes rebuild "$LINODE_ID" --image "$IMAGE_ID" --root_pass="$ROOT_PASS";
linode-cli linodes config-update "$LINODE_ID" "$CONFIG_ID" --kernel "linode/grub2" --booted false;
linode-cli linodes boot "$LINODE_ID" --config_id "$CONFIG_ID";
```
### Create a new Linode, upload image, and boot from it
```bash
nix build .#libu-linode --impure;
nix-shell -p linode-cli spwgen jq;
export ROOT_PASS="$(spwgen uldn 16)"
echo "$ROOT_PASS"

# Upload the built NixOS image
linode-cli image-upload --label "libu-nix" --description "libu deployed to NixOS" --region "us-ord" result/nixos.img.gz;
export IMAGE_ID="$(linode-cli images list --text | awk '/libu-nix/{print $1}' | awk '{for (i=1; i<=NF; i++) last=$i} END {print last}')";
echo "imageid: $IMAGE_ID";

# Create a new Linode from the uploaded custom image
export LINODE_ID="$(linode-cli linodes create \
  --label "libu-nix" \
  --region "us-ord" \
  --type "g6-nanode-1" \
  --image "$IMAGE_ID" \
  --root_pass "$ROOT_PASS" \
  --booted false \
  --json | jq -r '.[0].id')"
echo "linodeid: $LINODE_ID";

# Find and update the default config to use Linode GRUB, then boot it
export CONFIG_ID="$(linode-cli linodes configs-list "$LINODE_ID" --json | jq -r '.[0].id')"
echo "configid: $CONFIG_ID";
linode-cli linodes config-update "$LINODE_ID" "$CONFIG_ID" --kernel "linode/grub2" --booted false;
linode-cli linodes boot "$LINODE_ID" --config_id "$CONFIG_ID";
```
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
aws s3api put-bucket-policy --bucket nixos-iam-bucket --policy file://nix/bucket-policy.json; # add the bucket policy
aws iam create-role --role-name vmimport --assume-role-policy-document file://nix/vmimport-trust-policy.json # First create the role with the trust policy
aws iam put-role-policy --role-name vmimport --policy-name vmimport-policy --policy-document file://nix/vmimport-policy.json # Then attach the permission policy (not the trust policy)
aws ec2 import-snapshot --description "Imported nixos VHD" --disk-container file://nix/containers.json | cat; # import the image as an iam
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
    --block-device-mappings "file://nix/block-mapping.json"

```
the import-image command might take 30ish minutes to run, so there's probably a better way of creating the new IAM, maybe even just having the nixos config as a public or private flake and running nixos-rebuild switch on the ec2 instance machine with the flake as the target
# Rebuilding
```bash
export host="YOUR_HOSTNAME_OR_IP_HERE";
nixos-rebuild switch \
  --flake ".#libu-linode" \
  --target-host "master@$host" \
  --use-remote-sudo
```
