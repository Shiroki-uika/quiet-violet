/** Quiet Violet · Claude CLI 原色，Quiet Light 紫色界面。 */
interface ThemePreference {
  name: string;
  mode: "light" | "dark";
  followSystem: boolean;
}

const ACCENT = "#705697";
const CLI_VERSION = "2.1.322";

export function describeTheme(preference: ThemePreference): string {
  // 浅色 GitHub 粉蓝；深色 Monokai；Diff 蓝色新增、粉红删除。
  const { name, mode, followSystem } = preference;
  if (!followSystem) return `${name} · 手动切换`;
  return `${name} · ${mode} · 跟随系统`;
}

const preview: ThemePreference = {
  name: "Quiet Violet",
  mode: "light",
  followSystem: true,
};

console.log(describeTheme(preview), ACCENT, CLI_VERSION);
