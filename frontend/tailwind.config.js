/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eef4ff", 100: "#d9e6ff", 300: "#8fb6ff",
          500: "#3b6fff", 600: "#2456e6", 700: "#1b42b8",
        },
      },
    },
  },
  plugins: [],
};
