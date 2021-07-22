# Image configuration

Image configuration consists of two sections - Disks and SystemConfigs - that describe the produced artifact(image). Image configuration code can be found in (configuration.go)[../../tools/imagegen/configuration/configuration.go] and validity of the configuration file can be verified by the [imageconfigvalidator](../../tools/imageconfigvalidator/imageconfigvalidator.go)


## Disks
Disks entry specifies the disk configuration like its size (for virtual disks), partitions and partition table.

### Artifacts
Artifact (non-ISO image building only) defines the name, type and optional compression of the output CBL-Mariner image.

Sample Artifacts entry, creating a raw rootfs, compressed to .tar.gz format(note that this format does not support partitions, so there would be no "Partitions" entry):

``` json
"Artifacts": [
    {
        "Name": "core",
        "Compression": "tar.gz"
    }
]

```
Sample Artifacts entry, creating a vhdx disk image:

``` json
"Artifacts": [
    {
        "Name": "otherName",
        "Type": "vhdx"
    }
],
```

### Partitions
"Partitions" key holds an array of Partition entries.

Partition defines the size, name and file system type for a partition.
"Start" and "End" fields define the offset from the beginning of the disk in MBs.
An "End" value of 0 will determine the size of the partition using the next
partition's start offset or the value defined by "MaxSize", if this is the last
partition on the disk.

Note that Partitions do not have to be provided; the resulting image is going to be a rootfs.

Sample partitions entry, specifying a boot partition and a root partition:

``` json
"Partitions": [
    {
        "ID": "boot",
        "Flags": [
            "esp",
            "boot"
        ],
        "Start": 1,
        "End": 9,
        "FsType": "fat32"
    },
    {
        "ID": "rootfs",
        "Start": 9,
        "End": 0,
        "FsType": "ext4"
    }
]
```

#### Flags
"Flags" key controls special handling for certain partitions.

- `esp` indicates this is the UEFI esp partition
- `grub` indicates this is a grub boot partition
- `bios_grub` indicates this is a bios grub boot partition
- `boot` indicates this is a boot partition
- `dmroot` indicates this partition will be used for a device mapper root device (i.e. `Encryption` or `ReadOnlyVerityRoot`)

## SystemConfigs

SystemConfigs is an array of SystemConfig entries.

SystemConfig defines how each system present on the image is supposed to be configured.

### PartitionSettings

PartitionSettings key is an array of PartitionSetting entries.

PartitionSetting holds the mounting information for each partition.

A sample PartitionSettings entry, designating an EFI and a root partitions:

``` json
"PartitionSettings": [
    {
        "ID": "boot",
        "MountPoint": "/boot/efi",
        "MountOptions" : "umask=0077"
    },
    {
        "ID": "rootfs",
        "MountPoint": "/"
    }
],
```

It is possible to use `PartitionSettings` to configure diff disk image creation. Two types of diffs are possible.
`rdiff` and `overlay` diff.

For small and deterministic images `rdiff` is a better algorithm.
For large images based on `ext4` `overlay` diff is a better algorithm.

A sample `ParitionSettings` entry using `rdiff` algorithm:

``` json
{
    "ID": "boot",
    "MountPoint": "/boot/efi",
    "MountOptions" : "umask=0077",
    "RdiffBaseImage" : "../out/images/core-efi/core-efi-1.0.20200918.1751.ext4"
},
 ```

A sample `ParitionSettings` entry using `overlay` algorithm:

``` json
{
   "ID": "rootfs",
   "MountPoint": "/",
   "OverlayBaseImage" : "../out/images/core-efi/core-efi-rootfs-1.0.20200918.1751.ext4"
}

```
`RdiffBaseImage` represents the base image when `rdiff` algorithm is used.
`OverlayBaseImage` represents the base image when `overlay` algorithm is used.

### PackageLists

PackageLists key consists of an array of relative paths to the package lists (JSON files).

All of the files listed in PackageLists are going to be scanned in a linear order to obtain a final list of packages for the resulting image by taking a union of all packages. **It is recommended that initramfs is the last package to speed up the installation process.**

PackageLists **must not include kernel packages**! To provide a kernel, use KernelOptions instead. Providing a kernel package in any of the PackageLists files results in an **undefined behavior**.

If any of the packages depends on a kernel, make sure that the required kernel is provided with KernelOptions.

A sample PackageLists entry pointing to three files containing package lists:
``` json
"PackageLists": [
    "packagelists/hyperv-packages.json",
    "packagelists/core-packages-image.json",
    "packagelists/cloud-init-packages.json"
],
```
### RemoveRpmDb

RemoveRpmDb triggers RPM database removal after the packages have been installed.
Removing the RPM database may break any package managers inside the image.


### KernelOptions

KernelOptions key consists of a map of key-value pairs, where a key is an identifier and a value is a name of the package (kernel) used in a scenario described by the identifier. During the build time, all kernels provided in KernelOptions will be built.

KernelOptions is mandatory for all non-`rootfs` image types.

KernelOptions may be included in `rootfs` images which expect a kernel, such as the initrd for an ISO, if desired.

Currently there are only two keys with an assigned meaning:
- `default` key needs to be always provided. It designates a kernel that is used when no other scenario is applicable (i.e. by default).
- `hyperv` key is an optional key that is only meaningful in ISO context. It provides a kernel that will be chosen by the installer instead of the default one if the installer detects that the installation is conducted in the Hyper-V environment.


Keys starting with an underscore are ignored - they can be used for providing comments.

A sample KernelOptions specifying a default kernel:

``` json
"KernelOptions": {
    "default": "kernel-hyperv"
},
```

A sample KernelOptions specifying a default kernel and a specialized kernel for Hyper-V scenario:

``` json
"KernelOptions": {
    "default": "kernel",
    "hyperv": "kernel-hyperv"
},
```

### ReadOnlyVerityRoot
"ReadOnlyVerityRoot" key controls making the root filesystem read-only using dm-verity.
It will create a verity disk from the partition mounted at "/". The verity data is stored as
part of the image's initramfs. More details can be found in [Misc: Read Only Roots](../how_it_works/5_misc.md#dm-verity-read-only-roots)

#### Considerations
Having a read-only root filesystem will change the behavior of the image in some fundamental ways. There are several areas that should be considered before enabling a read-only root:

##### Writable Data
Any writable data which needs to be preserved will need to be stored into a separate writable partition. The `TmpfsOverlays` key will create throw-away writable partitions which are reset on every boot. The example configs create an overlay on `/var`, but the more refined the overlays are, the more secure they will be.

##### GPL Licensing
If using a read-only root in conjunction with a verified boot flow that uses a signed initramfs, carefully consider the implications on GPLv3 code. The read-only nature of the filesystem means a user cannot replace GPLv3 components without re-signing a new initramfs.

##### Users
Since users are controlled by files in `/etc`, these files are read-only when this is set. It is recommended to either use SSH key based login or pre-hash the password to avoid storing passwords in plain text in the config files (See [Users](#users)).

##### Separate `/boot` Partition
Since the root partition's hash tree is stored as part of the initramfs, the initramfs cannot be stored on the same root partition (it would invalidate the measurements). To avoid this a separate `/boot` partition is needed to house the hash tree (via the initramfs).

##### ISO
The ISO command line installer supports enabling read-only roots if they are configured through the configuration JSON file (see [full.json's](../../imageconfigs/full.json) `"CBL-Mariner Core Read-Only"` entry). The automatic partition creation mode will create the required `/boot` partition if the read-only root is enabled.

The GUI installer does not currently support read-only roots.
- `Enable`: Enable dm-verity on the root filesystem
- `Name`: Custom name for the mounted root (default is `"verity_root_fs"`)
- `ErrorCorrectionEnable`: Enable automatic error correction of modified blocks (default is `true`)
- `ErrorCorrectionEncodingRoots`: Increase overhead to increase resiliency of the forward error correction (default is `2` bytes of code per 255 bytes of data)
- `RootHashSignatureEnable`: Validate the root hash against a key stored in the kernel's system keyring. The signature file should be called `<Name>.p7` and must be stored in the initramfs. This signature WILL NOT BE included automatically in the initramfs. It must be included via an out of band build step.
- `ValidateOnBoot`: Run a validation of the full disk at boot time, normally blocks are validated only as needed. This can take several minutes if the disk is corrupted.
- `VerityErrorBehavior`: Indicate additional special system behavior when encountering an unrecoverable verity corruption. One of `"ignore"`, `"restart"`, `"panic"`. Normal behavior is to return an IO error when reading corrupt blocks.
- `TmpfsOverlays`: Mount these paths as writable overlays backed by a tmpfs in memory.
- `TmpfsOverlaySize`: Maximum amount of memory the overlays may use. Maybe be one of three forms: `"1234"`, `"1234[k,m,g]"`, `"20%"` (default is `"20%"`) 
- `TmpfsOverlayDebugEnabled`: Make the tmpfs overlay mounts easily accessible for debugging purposes. They can be found in /mnt/verity_overlay_debug_tmpfs. Include the
    `verity-read-only-root-debug-tools` package to create the required mount points.

A sample ReadOnlyVerityRoot specifying a basic read-only root using default error correction. This configuration may be used for both normal images and ISO configurations:
``` json
"ReadOnlyVerityRoot": {
    "Enable": true,
    "TmpfsOverlays": [
        "/var"
    ],
},
```

### KernelCommandLine

KernelCommandLine is an optional key which allows additional parameters to be passed to the kernel when it is launched from Grub.

ImaPolicy is a list of Integrity Measurement Architecture (IMA) policies to enable, they may be any combination of `tcb`, `appraise_tcb`, `secure_boot`.

ExtraCommandLine is a string which will be appended to the end of the kernel command line and may contain any additional parameters desired. The `` ` `` character is reserved and may not be used.

A sample KernelCommandLine enabling a basic IMA mode and passing two additional parameters:

``` json
"KernelCommandLine": {
    "ImaPolicy": ["tcb"],
    "ExtraCommandLine": "my_first_param=foo my_second_param=\"bar baz\""
},
```

### HidepidDisabled

An optional flag that removes the `hidepid` option from `/proc`. `Hidepid` prevents proc IDs from being visible to all users. Set this flag if mounting `/proc` in postinstall scripts to ensure the mount options are set correctly.

### Users

Users is an array of user information. The User information is a map of key value pairs.

The image generated has users matching the values specified in Users.

The table below are the keys for the users.

|Key                |Type               |Restrictions
--------------------|:------------------|:------------------------------------------------
|Name               |string             |Cannot be empty
|UID                |string             |Must be in range 0-60000
|PasswordHashed     |bool               |
|Password           |string             |
|PasswordExpiresDays|number             |Must be in range 0-99999 or -1 for no expiration
|SSHPubKeyPaths     |array of strings   |
|PrimaryGroup       |string             |
|SecondaryGroups    |array of strings   |
|StartupCommand     |string             |

An example usage for users "root" and "basicUser" would look like:

``` json
"Users": [
    {
        "Name": "root",
        "Password": "somePassword"
    },
    {
        "Name": "basicUser",
        "Password": "someOtherPassword",
        "UID": 1001
    }
]
```

# Sample image configuration

A sample image configuration, producing a VHDX disk image:

``` json
{
    "Disks": [
        {
            "PartitionTableType": "gpt",
            "MaxSize": 11264,
            "Artifacts": [
                {
                    "Name": "core",
                    "Type": "vhdx"
                }
            ],
            "Partitions": [
                {
                    "ID": "boot",
                    "Flags": [
                        "esp",
                        "boot"
                    ],
                    "Start": 1,
                    "End": 9,
                    "FsType": "fat32"
                },
                {
                    "ID": "rootfs",
                    "Start": 9,
                    "End": 0,
                    "FsType": "ext4"
                }
            ]
        }
    ],
    "SystemConfigs": [
        {
            "Name": "Standard",
            "BootType": "efi",
            "PartitionSettings": [
                {
                    "ID": "boot",
                    "MountPoint": "/boot/efi",
                    "MountOptions" : "umask=0077",
                    "RdiffBaseImage" : "../out/images/core-efi/core-efi-1.0.20200918.1751.ext4"
                },
                {
                    "ID": "rootfs",
                    "MountPoint": "/",
                     "OverlayBaseImage" : "../out/images/core-efi/core-efi-rootfs-1.0.20200918.1751.ext4"
                }
            ],
            "PackageLists": [
                "packagelists/hyperv-packages.json",
                "packagelists/core-packages-image.json",
                "packagelists/cloud-init-packages.json"
            ],
            "KernelOptions": {
                "default": "kernel"
            },
            "KernelCommandLine": {
                "ImaPolicy": ["tcb"],
                "ExtraCommandLine": "my_first_param=foo my_second_param=\"bar baz\""
            },
            "Hostname": "cbl-mariner"
        }
    ]
}

```
