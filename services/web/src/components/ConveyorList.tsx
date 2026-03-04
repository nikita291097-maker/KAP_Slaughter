import Conveyor from './Conveyor';

const conveyors = [
  'Конвейер обескровливания',
  'Элеватор опуска в шпарильную установку',
  'Конвейер разделочный',
  'Конвейер для органов',
  'Конвейер шокового туннеля'
] as const;

export default function ConveyorList() {
  return (
    <section className="conveyor-list" aria-label="Мнемосхема конвейеров">
      {conveyors.map((name) => (
        <Conveyor key={name} name={name} load={0} />
      ))}
    </section>
  );
}
