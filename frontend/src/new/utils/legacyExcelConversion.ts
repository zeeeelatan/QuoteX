import axios from 'axios'

const OLE_SIGNATURE = [0xd0, 0xcf, 0x11, 0xe0, 0xa1, 0xb1, 0x1a, 0xe1]

export function isLegacyXls(bytes: Uint8Array): boolean {
  return bytes.length >= OLE_SIGNATURE.length &&
    OLE_SIGNATURE.every((value, index) => bytes[index] === value)
}

export function toConvertedXlsxFileName(fileName: string): string {
  const displayNameMatch = fileName.match(/[?&]displayName=([^&]+)/i)
  if (displayNameMatch?.[1]) {
    let displayName = displayNameMatch[1]
    try {
      displayName = decodeURIComponent(displayName)
    } catch {
      // 保留无法解码的原文本
    }
    return /\.xls$/i.test(displayName)
      ? displayName.replace(/\.xls$/i, '.xlsx')
      : `${displayName}.xlsx`
  }
  if (/\.xls$/i.test(fileName)) return fileName.replace(/\.xls$/i, '.xlsx')
  return `${fileName.replace(/\.[^.]*$/, '') || 'converted'}.xlsx`
}

export function bytesToBase64(bytes: Uint8Array): string {
  let binary = ''
  const chunkSize = 0x8000
  for (let i = 0; i < bytes.length; i += chunkSize) {
    binary += String.fromCharCode(...bytes.subarray(i, i + chunkSize))
  }
  return btoa(binary)
}

export async function convertLegacyXls(
  bytes: Uint8Array,
  fileName: string,
  apiUrl: string
): Promise<{ bytes: Uint8Array; fileName: string }> {
  const formData = new FormData()
  formData.append(
    'file',
    new Blob([bytes], { type: 'application/vnd.ms-excel' }),
    fileName || 'source.xls'
  )
  const response = await axios.post(`${apiUrl}/document/convert-excel`, formData, {
    responseType: 'arraybuffer',
    timeout: 130000,
  })
  const convertedBytes = new Uint8Array(response.data)
  return {
    bytes: convertedBytes,
    fileName: toConvertedXlsxFileName(fileName),
  }
}
