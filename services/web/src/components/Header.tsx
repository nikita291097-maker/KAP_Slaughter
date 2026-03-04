import { useEffect, useState } from 'react';

function formatDateTime(date: Date): string {
  const pad = (value: number) => String(value).padStart(2, '0');

  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(
    date.getHours()
  )}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
}

export default function Header() {
  const [dateTime, setDateTime] = useState(() => formatDateTime(new Date()));

  useEffect(() => {
    const timerId = window.setInterval(() => {
      setDateTime(formatDateTime(new Date()));
    }, 1000);

    return () => {
      window.clearInterval(timerId);
    };
  }, []);

  return (
    <header className="header">
      <h1 className="header__title">КАП. Убой</h1>
      <time className="header__time" dateTime={new Date().toISOString()}>
        {dateTime}
      </time>
    </header>
  );
}
