"""Maps plaso objects into CASE equivalent objects."""

from dfvfs.lib import definitions as dfvfs_definitions

from case import CASE

# Maps dfvfs compression methods to CASE CompressionMethod
CompressionMethod = {
    dfvfs_definitions.COMPRESSION_METHOD_BZIP2: CASE.BZIP2,
    dfvfs_definitions.COMPRESSION_METHOD_DEFLATE: CASE.Deflate,
    dfvfs_definitions.COMPRESSION_METHOD_LZMA: CASE.LZMA,
    dfvfs_definitions.COMPRESSION_METHOD_XZ: CASE.XZ,
    dfvfs_definitions.COMPRESSION_METHOD_ZLIB: CASE.ZLIB,
    # GZIP is treated as a "file system" type in dfvfs instead of compression method.
    # The code mapping this will have to take this into account.
    dfvfs_definitions.TYPE_INDICATOR_GZIP: CASE.GZIP
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
# TODO: Is there a way to map EXT4 and NTFS? There is no type indicator for them.
# Their type indicator falls under "TSK_PARITION".
FileSystemType = {
    dfvfs_definitions.TYPE_INDICATOR_BDE: CASE.BDEVolume,
    dfvfs_definitions.TYPE_INDICATOR_CPIO: CASE.CPIO,
    dfvfs_definitions.TYPE_INDICATOR_EWF: CASE.EWF,
    dfvfs_definitions.TYPE_INDICATOR_NTFS: CASE.NTFS,
    dfvfs_definitions.TYPE_INDICATOR_TAR: CASE.TAR,
    dfvfs_definitions.TYPE_INDICATOR_VSHADOW: CASE.VSSVolume,
    dfvfs_definitions.TYPE_INDICATOR_ZIP: CASE.ZIP
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
