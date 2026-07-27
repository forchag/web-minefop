/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./apps/**/*.py",
    "./static/js/**/*.js",
  ],
  // Bootstrap already provides a CSS reset; disabling Tailwind's preflight
  // avoids the two frameworks fighting over base element styles.
  corePlugins: {
    preflight: false,
  },
  theme: {
    extend: {
      colors: {
        cm: {
          green: "#04502C",
          "green-dark": "#023018",
          red: "#CE1126",
          yellow: "#FCD116",
        },
      },
      fontFamily: {
        sans: ["'Inter'", "system-ui", "-apple-system", "sans-serif"],
        serif: ["'Merriweather'", "Georgia", "serif"],
      },
    },
  },
  plugins: [],
};
