export default function AppLogoIcon(props) {
  return (
    <svg
      {...props}
      viewBox="0 0 240 40"
      xmlns="http://www.w3.org/2000/svg"
      fill="currentColor"
    >
      {/* Logo M Geometris */}
      <g>
        <path
          d="M5 30V10L15 22L25 10V30H21V18L15 26L9 18V30H5Z"
          fill="currentColor"
        />
      </g>

      {/* Teks Managerku */}
      <text
        x="35"
        y="28"
        fontFamily="Inter, sans-serif"
        fontSize="24"
        fontWeight="700"
        letterSpacing="0.5"
        fill="currentColor"
      >
        Managerku
      </text>
    </svg>
  );
}
