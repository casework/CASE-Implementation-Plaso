"""Maps plaso objects into CASE equivalent objects."""

from dfvfs.lib import definitions as dfvfs_definitions

from case import CASE

# Maps dfvfs compression methods to CASE CompressionMethod
CompressionMethod = {
    dfvfs_definitions.COMPRESSION_METHOD_BZIP2: CASE.BZIP2,
    dfvfs_definitions.COMPRESSION_METHOD_DEFLATE: CASE.Deflate,
    dfvfs_definitions.COMPRESSION_METHOD_LZMA: CASE.LZMA,
    dfvfs_definitions.COMPRESSION_METHOD_XZ: CASE.XZ,
    dfvfs_definitions.COMPRESSION_METHOD_ZLIB: CASE.ZLIB
}

EncodingMethod = {
    dfvfs_definitions.ENCODING_METHOD_BASE16: CASE.Base16,
    dfvfs_definitions.ENCODING_METHOD_BASE32: CASE.Base32,
    dfvfs_definitions.ENCODING_METHOD_BASE64: CASE.Base64
}

EncryptionMethod = {
    dfvfs_definitions.ENCRYPTION_METHOD_BLOWFISH: CASE.Blowfish,
    dfvfs_definitions.ENCRYPTION_METHOD_DES3: CASE.DES3,
    dfvfs_definitions.ENCRYPTION_METHOD_AES: CASE.AES,
    dfvfs_definitions.ENCRYPTION_METHOD_RC4: CASE.RC4
}

EncryptionMode = {
    dfvfs_definitions.ENCRYPTION_MODE_OFB: CASE.OFB,
    dfvfs_definitions.ENCRYPTION_MODE_CFB: CASE.CFB,
    dfvfs_definitions.ENCRYPTION_MODE_ECB: CASE.ECB,
    dfvfs_definitions.ENCRYPTION_MODE_CBC: CASE.CBC
}

# Maps path spec type indicator to CASE FileSystemType
# TODO: Is there a way to map EXT4? There is no type indicator for them.
# Their type indicator falls under "TSK_PARITION".
# NOTE: This will be used for the "File" property bundle. Even though some of these
#       file systems types don't have properties like
#        "filePath", they are still considered a file system because they have
#       other characteristics like MAC times or are just a "container of files".
#       (The property bundle is just badly named. Think of "File" more like "FileStat")
#       There are however, exceptions for a few like SQLiteBlob, Encrypted Stream, and
#       Compression (except GZIP I think), because they wouldn't have any filestat info? maybe? who knows?
FileSystemType = {
    dfvfs_definitions.TYPE_INDICATOR_BDE: CASE.BDE,
    dfvfs_definitions.TYPE_INDICATOR_CPIO: CASE.CPIO,
    dfvfs_definitions.TYPE_INDICATOR_EWF: CASE.EWF,
    dfvfs_definitions.TYPE_INDICATOR_LVM: CASE.LVM,
    dfvfs_definitions.TYPE_INDICATOR_NTFS: CASE.NTFS,
    dfvfs_definitions.TYPE_INDICATOR_QCOW: CASE.QCOW,
    dfvfs_definitions.TYPE_INDICATOR_RAW: CASE.RAW,
    dfvfs_definitions.TYPE_INDICATOR_SQLITE_BLOB: CASE.SQLite,
    dfvfs_definitions.TYPE_INDICATOR_TAR: CASE.TAR,
    dfvfs_definitions.TYPE_INDICATOR_VHDI: CASE.VHDI,
    dfvfs_definitions.TYPE_INDICATOR_VMDK: CASE.VMDK,
    dfvfs_definitions.TYPE_INDICATOR_VSHADOW: CASE.VSSVolume,
    dfvfs_definitions.TYPE_INDICATOR_ZIP: CASE.ZIP
}

ImageType = {
    dfvfs_definitions.TYPE_INDICATOR_VMDK: CASE.VMDK,
    dfvfs_definitions.TYPE_INDICATOR_VHDI: CASE.VHDI,
    dfvfs_definitions.TYPE_INDICATOR_EWF: CASE.EWF,
    dfvfs_definitions.TYPE_INDICATOR_RAW: CASE.RAW,
    dfvfs_definitions.TYPE_INDICATOR_QCOW: CASE.QCOW
}

# Maps dfvfs path spec type indicators to type of relationship.
# (All non-hits will use '_default' key.)
kindOfRelationship = {
    '_default': 'contained-within',
    dfvfs_definitions.TYPE_INDICATOR_COMPRESSED_STREAM: 'decompressed-from',
    dfvfs_definitions.TYPE_INDICATOR_ENCODED_STREAM: 'decoded-from',
    dfvfs_definitions.TYPE_INDICATOR_ENCRYPTED_STREAM: 'decrypted-from'
}

# Maps plaso hash event attributes.
HashMethod = {
    'sha1_hash': CASE['SHA-1'],
    'sha256_hash': CASE.SHA256,
    'md5_hash': CASE.MD5
}
