import { ref, watch } from 'vue'

export type ColorMode = 'light' | 'dark' | 'system'

const STORAGE_KEY = 'pivot_color_mode'

const colorMode = ref<ColorMode>(
  (localStorage.getItem(STORAGE_KEY) as ColorMode) || 'system',
)

const resolvedDark = ref(false)

function applyMode() {
  const mode = colorMode.value
  let dark = false

  if (mode === 'dark') {
    dark = true
  } else if (mode === 'system') {
    dark = window.matchMedia('(prefers-color-scheme: dark)').matches
  }

  resolvedDark.value = dark
  document.documentElement.classList.toggle('dark', dark)
}

function setColorMode(mode: ColorMode) {
  colorMode.value = mode
  localStorage.setItem(STORAGE_KEY, mode)
  applyMode()
}

function hexToRgb(hex: string): [number, number, number] {
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  return [r, g, b]
}

function relativeLuminance(r: number, g: number, b: number): number {
  const [rs, gs, bs] = [r, g, b].map((c) => {
    const s = c / 255
    return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4)
  })
  return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs
}

function applyWorkspaceTheme(themeConfig: Record<string, string> | null) {
  const root = document.documentElement

  if (!themeConfig) {
    root.style.removeProperty('--primary')
    root.style.removeProperty('--primary-foreground')
    root.style.removeProperty('--ring')
    root.style.removeProperty('--accent')
    return
  }

  if (themeConfig.primary_color) {
    const hex = themeConfig.primary_color
    root.style.setProperty('--primary', hex)
    root.style.setProperty('--ring', hex)

    const [r, g, b] = hexToRgb(hex)
    const lum = relativeLuminance(r, g, b)
    root.style.setProperty('--primary-foreground', lum > 0.4 ? '#0f172a' : '#fafafa')
  }

  if (themeConfig.accent_color) {
    root.style.setProperty('--accent', themeConfig.accent_color)
  }
}

function initTheme() {
  applyMode()

  const mq = window.matchMedia('(prefers-color-scheme: dark)')
  mq.addEventListener('change', () => {
    if (colorMode.value === 'system') applyMode()
  })
}

export function useTheme() {
  return {
    colorMode,
    resolvedDark,
    setColorMode,
    applyWorkspaceTheme,
    initTheme,
  }
}
