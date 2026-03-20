export default function MandalaBackground() {
  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden z-0" aria-hidden>
      {/* Rotating mandala — far right */}
      <svg
        className="mandala absolute top-1/2 -translate-y-1/2 right-[-12%] w-[640px] h-[640px] opacity-[0.035]"
        viewBox="0 0 200 200"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* 16-petal outer ring */}
        {Array.from({ length: 16 }).map((_, i) => (
          <ellipse
            key={`op-${i}`}
            cx="100" cy="100" rx="7" ry="46"
            fill="#FF8C00"
            transform={`rotate(${i * 22.5} 100 100)`}
            opacity="0.7"
          />
        ))}
        {/* 12-petal middle ring */}
        {Array.from({ length: 12 }).map((_, i) => (
          <ellipse
            key={`mp-${i}`}
            cx="100" cy="100" rx="5" ry="30"
            fill="#FFD700"
            transform={`rotate(${i * 30 + 15} 100 100)`}
            opacity="0.8"
          />
        ))}
        {/* 8-petal inner ring */}
        {Array.from({ length: 8 }).map((_, i) => (
          <ellipse
            key={`ip-${i}`}
            cx="100" cy="100" rx="4" ry="18"
            fill="#FF8C00"
            transform={`rotate(${i * 45 + 22.5} 100 100)`}
            opacity="0.9"
          />
        ))}
        {/* Geometric rings */}
        <circle cx="100" cy="100" r="92" stroke="#FF8C00" strokeWidth="0.4" fill="none" opacity="0.5" />
        <circle cx="100" cy="100" r="70" stroke="#FFD700" strokeWidth="0.3" fill="none" opacity="0.4" />
        <circle cx="100" cy="100" r="50" stroke="#FF8C00" strokeWidth="0.3" fill="none" opacity="0.4" />
        {/* Centre */}
        <circle cx="100" cy="100" r="12" fill="#FF8C00" opacity="0.5" />
        <circle cx="100" cy="100" r="6" fill="#FFD700" opacity="0.8" />
      </svg>

      {/* Second smaller mandala — top-left, counter-rotating */}
      <svg
        className="absolute top-[-5%] left-[-8%] w-[340px] h-[340px] opacity-[0.025]"
        style={{ animation: 'spin 120s linear infinite reverse' }}
        viewBox="0 0 200 200"
        fill="none"
      >
        {Array.from({ length: 12 }).map((_, i) => (
          <ellipse
            key={`sl-${i}`}
            cx="100" cy="100" rx="6" ry="40"
            fill="#FFD700"
            transform={`rotate(${i * 30} 100 100)`}
            opacity="0.6"
          />
        ))}
        <circle cx="100" cy="100" r="80" stroke="#FFD700" strokeWidth="0.4" fill="none" opacity="0.4" />
        <circle cx="100" cy="100" r="8" fill="#FFD700" opacity="0.7" />
      </svg>

      {/* Ambient gradient orbs */}
      <div className="absolute top-0 left-1/4 w-[500px] h-[500px] rounded-full
                      bg-purple-600/5 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-0 right-1/3 w-[400px] h-[400px] rounded-full
                      bg-saffron/5 blur-[100px] pointer-events-none" />
    </div>
  )
}
