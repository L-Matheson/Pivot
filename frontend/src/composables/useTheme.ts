import { useDark, useToggle } from '@vueuse/core'

// color mode

const isDark = useDark({ storageKey: 'pivot_color_mode' })
const toggleDark = useToggle(isDark)

// color math

function hexToRgb(hex: string): [number, number, number] {
  const red = parseInt(hex.slice(1, 3), 16)
  const green = parseInt(hex.slice(3, 5), 16)
  const blue = parseInt(hex.slice(5, 7), 16)
  return [red, green, blue]
}

function relativeLuminance(red: number, green: number, blue: number): number {
  const [linearRed, linearGreen, linearBlue] = [red, green, blue].map((channel) => {
    const normalized = channel / 255
    return normalized <= 0.03928 ? normalized / 12.92 : Math.pow((normalized + 0.055) / 1.055, 2.4)
  })
  return 0.2126 * linearRed + 0.7152 * linearGreen + 0.0722 * linearBlue
}

// workspace theme

function applyWorkspaceTheme(themeConfig: Record<string, string> | null) {
  const root = document.documentElement

  if (!themeConfig) {
    root.style.removeProperty('--primary')
    root.style.removeProperty('--primary-foreground')
    root.style.removeProperty('--ring')
    root.style.removeProperty('--accent')
    root.style.removeProperty('--accent-foreground')
    return
  }

  if (themeConfig.primary_color) {
    const hex = themeConfig.primary_color
    root.style.setProperty('--primary', hex)
    root.style.setProperty('--ring', hex)

    const [red, green, blue] = hexToRgb(hex)
    const luminance = relativeLuminance(red, green, blue)
    root.style.setProperty('--primary-foreground', luminance > 0.4 ? '#0f172a' : '#fafafa')
  }

  if (themeConfig.accent_color) {
    const hex = themeConfig.accent_color
    root.style.setProperty('--accent', hex)
    const [red, green, blue] = hexToRgb(hex)
    const luminance = relativeLuminance(red, green, blue)
    root.style.setProperty('--accent-foreground', luminance > 0.4 ? '#0f172a' : '#fafafa')
  }
}

export function useTheme() {
  return {
    isDark,
    toggleDark,
    applyWorkspaceTheme,
  }
}
