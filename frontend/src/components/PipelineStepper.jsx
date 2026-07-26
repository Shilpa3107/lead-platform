// frontend/src/components/PipelineStepper.jsx
const STAGES = ['new', 'contacted', 'qualified', 'won'];

export default function PipelineStepper({ status }) {
  if (status === 'lost') {
    return <div className="pipeline-labels"><span style={{ color: 'var(--status-lost)', fontWeight: 500 }}>Lost</span></div>;
  }
  const currentIndex = STAGES.indexOf(status);
  return (
    <div>
      <div className="pipeline-stepper">
        {STAGES.map((stage, i) => (
          <div className="pipeline-step" key={stage}>
            <div className={`pipeline-dot ${i === currentIndex ? 'active' : i < currentIndex ? 'passed' : ''}`} />
            {i < STAGES.length - 1 && <div className={`pipeline-line ${i < currentIndex ? 'passed' : ''}`} />}
          </div>
        ))}
      </div>
      <div className="pipeline-labels">
        {STAGES.map((s) => <span key={s}>{s}</span>)}
      </div>
    </div>
  );
}