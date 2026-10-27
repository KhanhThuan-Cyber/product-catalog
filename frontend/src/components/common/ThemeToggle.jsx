import { useTheme } from '../../context/ThemeContext'

/**
 * Nút chuyển dark ↔ light — có thể dùng ở bất kỳ đâu.
 * Không cần props, tự lấy theme từ context.
 */
export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme()
  const isDark = theme === 'dark'

  return (
    <button
      className="theme-toggle btn btn-sm btn-outline"
      onClick={toggleTheme}
      title={isDark ? 'Chuyển sang giao diện sáng' : 'Chuyển sang giao diện tối'}
      aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      style={{ gap: 6 }}
    >
      {isDark ? (
        <>
          <i className="fa-solid fa-sun" style={{ color: 'var(--accent-amber)' }}></i>
          <span>Sáng</span>
        </>
      ) : (
        <>
          <i className="fa-solid fa-moon" style={{ color: 'var(--accent-violet)' }}></i>
          <span>Tối</span>
        </>
      )}
    </button>
  )
}
