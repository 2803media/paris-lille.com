/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./data.js"],
  darkMode: "selector",
  theme: {
    extend: {
      animation: {
        heartbeat: "heartbeat 2s ease-in-out infinite",
        "swipe-hint": "swipe-hint 2.5s ease-in-out forwards",
      },
      keyframes: {
        heartbeat: {
          "0%, 100%": { transform: "scale(1)" },
          "50%": { transform: "scale(1.15)" },
        },
        "swipe-hint": {
          "0%": { opacity: "0", transform: "translateX(20px)" },
          "15%": { opacity: "1", transform: "translateX(0)" },
          "50%": { opacity: "1", transform: "translateX(-40px)" },
          "80%": { opacity: "0", transform: "translateX(-40px)" },
          "100%": { opacity: "0", pointerEvents: "none" },
        },
      },
    },
  },
};
