/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(0 0% 0%)",
        background: "hsl(0 0% 98%)",
        foreground: "hsl(0 0% 5%)",
        primary: {
          DEFAULT: "hsl(0 0% 0%)",
          foreground: "hsl(0 0% 100%)",
        },
        secondary: {
          DEFAULT: "hsl(0 0% 90%)",
          foreground: "hsl(0 0% 0%)",
        },
        accent: {
          DEFAULT: "hsl(0 0% 85%)",
          foreground: "hsl(0 0% 0%)",
        },
      },
      borderWidth: {
        '3': '3px',
        '4': '4px',
      },
      fontSize: {
        'xs': '0.75rem',
        'sm': '0.875rem',
        'base': '1rem',
        'lg': '1.125rem',
        'xl': '1.25rem',
        '2xl': '1.5rem',
        '3xl': '1.875rem',
        '4xl': '2.25rem',
      },
    },
  },
  plugins: [],
}

