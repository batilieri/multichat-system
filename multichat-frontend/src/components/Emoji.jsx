export default function Emoji({ children, style, ...props }) {
  return (
    <span
      className="emoji inline-flex items-center justify-center m-0 p-0 align-middle"
      style={{ lineHeight: 1, verticalAlign: 'middle', ...style }}
      {...props}
    >
      {children}
    </span>
  );
}