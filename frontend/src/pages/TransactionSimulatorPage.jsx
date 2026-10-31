import React, { useState } from 'react';
import {
  Activity,
  Play,
  CheckCircle2,
  XCircle,
  RotateCcw,
  ArrowRight,
  Clock,
  ShieldCheck,
  Server,
  Layers
} from 'lucide-react';
import { transactionsApi } from '../services/api';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

const SCENARIOS = [
  {
    id: 'SIMULATED_FAILURE_ROLLBACK',
    title: 'Failure Simulation & Atomic Rollback',
    description: 'Demonstrates ACID Atomicity. A record is inserted into an uncommitted buffer, an error triggers, and MySQL InnoDB ROLLBACK completely restores previous table state.',
    badge: 'ATOMIC TEST',
  },
  {
    id: 'COMMIT_SUCCESS',
    title: 'Multi-Step Atomic Commit',
    description: 'Demonstrates durability and consistency. Valid business operations run inside an active InnoDB transaction, and COMMIT writes changes permanently to disk.',
    badge: 'COMMIT TEST',
  },
  {
    id: 'SAVEPOINT_PARTIAL_ROLLBACK',
    title: 'Savepoint Partial Rollback',
    description: 'Demonstrates nested transaction savepoints. Record A is inserted, SAVEPOINT sp1 is set, invalid Record B is inserted, and ROLLBACK TO SAVEPOINT sp1 discards only Record B.',
    badge: 'SAVEPOINT TEST',
  },
];

export const TransactionSimulatorPage = () => {
  const [selectedScenario, setSelectedScenario] = useState('SIMULATED_FAILURE_ROLLBACK');
  const [running, setRunning] = useState(false);
  const [simulationResult, setSimulationResult] = useState(null);

  const handleRunSimulation = async (scenarioId) => {
    setSelectedScenario(scenarioId);
    setRunning(true);
    setSimulationResult(null);
    try {
      const res = await transactionsApi.runDemo(scenarioId);
      setSimulationResult(res.data);
    } catch (err) {
      alert(`Transaction simulation error: ${err.message}`);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="space-y-5 max-w-[1600px] mx-auto">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-200">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-slate-900 flex items-center gap-2">
            <Activity className="w-5 h-5 text-indigo-600" />
            DBMS Transaction & Rollback Simulator
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Interactive real-time demonstration of MySQL InnoDB ACID mechanics: START TRANSACTION, COMMIT, ROLLBACK, and SAVEPOINT.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs font-mono font-medium text-slate-700 px-2.5 py-1 rounded bg-slate-100 border border-slate-200">
            InnoDB ACID Engine
          </span>
        </div>
      </div>

      {/* Scenario Selection Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {SCENARIOS.map((sc) => {
          const isSelected = selectedScenario === sc.id;
          return (
            <div
              key={sc.id}
              onClick={() => setSelectedScenario(sc.id)}
              className={`panel p-4 cursor-pointer transition-all flex flex-col justify-between ${
                isSelected
                  ? 'border-indigo-600 bg-indigo-50/20 ring-1 ring-indigo-500 shadow-xs'
                  : 'hover:border-slate-300'
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-bold font-mono uppercase text-slate-500 tracking-wider">
                    {sc.badge}
                  </span>
                  {isSelected && <Badge variant="ACTIVE">Selected</Badge>}
                </div>
                <h3 className="text-sm font-semibold text-slate-900">{sc.title}</h3>
                <p className="mt-1.5 text-xs text-slate-500 leading-relaxed">{sc.description}</p>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-100">
                <Button
                  variant={isSelected ? 'primary' : 'secondary'}
                  size="sm"
                  icon={Play}
                  loading={running && selectedScenario === sc.id}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleRunSimulation(sc.id);
                  }}
                  className="w-full text-xs"
                >
                  Run Scenario
                </Button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Simulation Execution Timeline & Diagnostics */}
      {running ? (
        <LoadingSpinner label="Executing transaction statements inside InnoDB engine..." size="lg" />
      ) : simulationResult ? (
        <div className="space-y-4">
          {/* Outcome Summary Banner */}
          <div
            className={`panel p-4 ${
              simulationResult.overall_status === 'COMMITTED'
                ? 'border-emerald-200 bg-emerald-50/20'
                : 'border-slate-200 bg-slate-50/30'
            }`}
          >
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <div
                  className={`p-2.5 rounded-md border ${
                    simulationResult.overall_status === 'COMMITTED'
                      ? 'bg-emerald-50 border-emerald-200 text-emerald-700'
                      : 'bg-indigo-50 border-indigo-200 text-indigo-700'
                  }`}
                >
                  <Activity className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-sm font-bold text-slate-900 font-mono">
                      Outcome: {simulationResult.overall_status}
                    </h3>
                    <Badge variant={simulationResult.overall_status} />
                  </div>
                  <p className="text-xs text-slate-500 mt-0.5">{simulationResult.explanation}</p>
                </div>
              </div>

              {/* State Verification Metrics */}
              <div className="flex items-center gap-3.5 text-xs font-mono bg-white p-2.5 rounded-md border border-slate-200 shadow-xs">
                <div>
                  <span className="text-[10px] font-semibold text-slate-400 block uppercase">INITIAL ROWS</span>
                  <span className="text-slate-900 font-bold">{simulationResult.initial_state_count}</span>
                </div>
                <ArrowRight className="w-3.5 h-3.5 text-slate-400" />
                <div>
                  <span className="text-[10px] font-semibold text-slate-400 block uppercase">FINAL ROWS</span>
                  <span className="text-emerald-700 font-bold">{simulationResult.final_state_count}</span>
                </div>
                <div className="border-l border-slate-200 pl-3">
                  <span className="text-[10px] font-semibold text-slate-400 block uppercase">DURATION</span>
                  <span className="text-indigo-700 font-bold">{simulationResult.duration_ms} ms</span>
                </div>
              </div>
            </div>
          </div>

          {/* Step-by-Step Transaction Timeline */}
          <div className="panel p-5 space-y-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-2">
              <Clock className="w-4 h-4 text-indigo-600" /> InnoDB Transaction Step Timeline
            </h3>

            <div className="relative pl-6 space-y-4 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
              {simulationResult.steps.map((st) => {
                let badgeVariant = 'SUCCESS';
                let iconColor = 'bg-emerald-600 text-white';
                if (st.status === 'FAILED') {
                  badgeVariant = 'FAILED';
                  iconColor = 'bg-rose-600 text-white';
                } else if (st.status === 'ROLLED_BACK') {
                  badgeVariant = 'ROLLED_BACK';
                  iconColor = 'bg-indigo-600 text-white';
                } else if (st.status === 'SAVEPOINT_SET') {
                  badgeVariant = 'APPROVED';
                  iconColor = 'bg-blue-600 text-white';
                }

                return (
                  <div key={st.step_number} className="relative">
                    {/* Timeline Dot */}
                    <div
                      className={`absolute -left-[27px] top-1.5 w-5 h-5 rounded-full border-2 border-white flex items-center justify-center shadow-xs ${iconColor}`}
                    >
                      <span className="text-[10px] font-bold">{st.step_number}</span>
                    </div>

                    {/* Step Card */}
                    <div className="p-3.5 rounded-md bg-white border border-slate-200 space-y-2 shadow-xs">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <span className="text-xs font-bold font-mono text-slate-900">
                          {st.operation_name}
                        </span>
                        <Badge variant={st.status} />
                      </div>

                      <div className="p-2.5 rounded bg-slate-900 border border-slate-800 font-mono text-xs text-indigo-300 overflow-x-auto">
                        {st.sql}
                      </div>

                      <p className="text-xs text-slate-600">{st.details}</p>

                      {st.database_state_snapshot && (
                        <div className="text-[11px] font-mono text-slate-500 pt-2 border-t border-slate-100 flex items-center gap-2">
                          <span className="font-semibold text-slate-700">SNAPSHOT:</span>
                          <span className="text-indigo-700">{JSON.stringify(st.database_state_snapshot)}</span>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      ) : (
        <div className="panel p-12 text-center text-slate-500 text-xs">
          Select a transaction scenario above and click "Run Scenario" to execute live InnoDB statements with transaction isolation.
        </div>
      )}
    </div>
  );
};

export default TransactionSimulatorPage;
