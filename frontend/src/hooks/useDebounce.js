import { useEffect, useState } from 'react'

/**
 * Custom hook debounce giá trị đầu vào (ví dụ: chuỗi tìm kiếm) sau một khoảng delay.
 * @param {any} value Giá trị cần debounce
 * @param {number} delay Thời gian chờ (mặc định 400ms)
 * @returns {any} Giá trị đã được debounce
 */
export function useDebounce(value, delay = 400) {
  const [debouncedValue, setDebouncedValue] = useState(value)

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    return () => {
      clearTimeout(handler)
    }
  }, [value, delay])

  return debouncedValue
}
