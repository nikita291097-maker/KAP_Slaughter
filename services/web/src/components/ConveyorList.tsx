import Conveyor, { type ConveyorStatus } from './Conveyor';

type ConveyorData = {
  name: string;
  status: ConveyorStatus;
  load: number;
};

const conveyors: ConveyorData[] = [
  { name: 'Конвейер обескровливания', status: 'running', load: 72 },
  { name: 'Элеватор опуска в шпарильную установку', status: 'stopped', load: 0 },
  { name: 'Конвейер разделочный', status: 'error', load: 28 },
  { name: 'Конвейер для органов', status: 'warning', load: 41 },
  { name: 'Конвейер шокового туннеля', status: 'running', load: 66 }
];

export default function ConveyorList() {
  return (
    <section className="conveyor-list" aria-label="Мнемосхема конвейеров">
      {conveyors.map((conveyor) => (
        <Conveyor key={conveyor.name} name={conveyor.name} status={conveyor.status} load={conveyor.load} />
      ))}
    </section>
  );
}
