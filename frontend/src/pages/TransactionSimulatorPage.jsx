import React, { useState } from 'react';
import {
  Activity,
  Play,
  CheckCircle2,
  XCircle,
  RotateCcw,
  Flag,
  ArrowRight,
  Database,
  Clock,
  ShieldAlert,
  Info
} from 'lucide-react';
import { transactionsApi } from '../services/api';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

const SCENARIOS = [
  {
    id: 'SIMULATED_FAILURE_ROLLBACK',
    title: 'Failure Simulation & Atomic Rollback',
    description: 'Demonstrates ACID Atomicity. A record is inserted in an uncommitted transaction buffer, a simulated failure is encountered, and MySQL InnoDB ROLLBACK discards all uncommitted modifications completely.',
    badge: 'ATOMICTEST',
    color: 'border-rose-500/40 hover:border-rose-500',
  },
  {
    id: 'COMMIT_SUCCESS',
    title: 'Multi-Step Atomic Commit',
    description: 'Demonstrates normal durability and consistency. Valid operations are performed inside an active InnoDB transaction, and COMMIT writes the changes durably to the database tablespace.',
    badge: 'COMMITTEST',
    color: 'border-emerald-500/40 hover:border-emerald-500',
  },
  {
    id: 'SAVEPOINT_PARTIAL_ROLLBACK',
    title: 'Savepoint Partial Rollback',
    description: 'Demonstrates nested transaction savepoints. Record A is inserted, SAVEPOINT sp1 is set, invalid Record B is inserted, and ROLLBACK TO SAVEPOINT sp1 discards Record B while retaining Record A.',
    badge: 'SAVEPOINTTEST',
    color: 'border-purple-500/40 hover:border-purple-500',
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
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h2 className="text-2xl font-black tracking-tight text-white flex items-center gap-2">
            DBMS Transaction & Rollback Simulator
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Real interactive demonstration of MySQL InnoDB ACID mechanics: START TRANSACTION, COMMIT, ROLLBACK, and SAVEPOINT.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs font-mono text-emerald-400 px-2.5 py-1 rounded bg-emerald-500/10 border border-emerald-500/30">
            InnoDB ACID Engine
          </span>
        </div>
      </div>

      {/* Scenario Selection Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {SCENARIOS.map((sc) => {
          const isSelected = selectedScenario === sc.id;
          return (
            <div
              key={sc.id}
              onClick={() => setSelectedScenario(sc.id)}
              className={`p-5 rounded-2xl border glass-panel cursor-pointer transition-all flex flex-col justify-between ${
                isSelected
                  ? 'border-emerald-500 bg-emerald-500/5 shadow-xl shadow-emerald-950/20'
                  : `${sc.color} opacity-80 hover:opacity-100`
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-bold tracking-wider font-mono uppercase text-slate-400">
                    {sc.badge}
                  </span>
                  {isSelected && <Badge variant="ACTIVE">Selected</Badge>}
                </div>
                <h3 className="text-sm font-bold text-white">{sc.title}</h3>
                <p className="mt-2 text-xs text-slate-400 leading-relaxed">{sc.description}</p>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-800/80">
                <Button
                  variant={isSelected ? 'primary' : 'outline'}
                  size="sm"
                  icon={Play}
                  loading={running && selectedScenario === sc.id}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleRunSimulation(sc.id);
                  }}
                  className="w-full text-xs font-bold"
                >
                  Run Real Scenario
                </Button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Real Execution Timeline & Diagnostics */}
      {running ? (
        <LoadingSpinner label="Beginning InnoDB transaction, executing statements, and testing rollback..." size="lg" />
      ) : simulationResult ? (
        <div className="space-y-6">
          {/* Outcome Summary Banner */}
          <div className={`glass-panel p-5 rounded-2xl border ${
            simulationResult.overall_status === 'COMMITTED'
              ? 'border-emerald-500/50 bg-emerald-950/10'
              : 'border-purple-500/50 bg-purple-950/10'
          }`}>
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className={`p-3 rounded-xl border ${
                  simulationResult.overall_status === 'COMMITTED'
                    ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                    : 'bg-purple-500/10 border-purple-500/30 text-purple-400'
                }`}>
                  <Activity className="w-6 h-6" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-base font-bold text-white font-mono">
                      Transaction Outcome: {simulationResult.overall_status}
                    </h3>
                    <Badge variant={simulationResult.overall_status} />
                  </div>
                  <p className="text-xs text-slate-300 mt-0.5">{simulationResult.explanation}</p>
                </div>
              </div>

              {/* State Verification Pill */}
              <div className="flex items-center gap-4 text-xs font-mono bg-slate-900/80 p-3 rounded-xl border border-slate-800">
                <div>
                  <span className="text-slate-500 block text-[10px]">INITIAL ROWS</span>
                  <span className="text-slate-200 font-bold">{simulationResult.initial_state_count}</span>
                </div>
                <ArrowRight className="w-4 h-4 text-slate-600" />
                <div>
                  <span className="text-slate-500 block text-[10px]">FINAL ROWS</span>
                  <span className="text-emerald-400 font-bold">{simulationResult.final_state_count}</span>
                </div>
                <div className="border-l border-slate-800 pl-3">
                  <span className="text-slate-500 block text-[10px]">DURATION</span>
                  <span className="text-slate-300">{simulationResult.duration_ms} ms</span>
                </div>
              </div>
            </div>
          </div>

          {/* Step-by-Step Transaction Timeline */}
          <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-6">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200 flex items-center gap-2">
              <Clock className="w-4 h-4 text-emerald-400" /> InnoDB Transaction Step Timeline
            </h3>

            <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-3 before:bottom-3 before:w-0.5 before:bg-slate-800">
              {simulationResult.steps.map((st) => {
                let badgeVariant = 'SUCCESS';
                let iconColor = 'bg-emerald-500 text-white';
                if (st.status === 'FAILED') {
                  badgeVariant = 'FAILED';
                  iconColor = 'bg-rose-500 text-white';
                } else if (st.status === 'ROLLED_BACK') {
                  badgeVariant = 'ROLLED_BACK';
                  iconColor = 'bg-purple-500 text-white';
                } else if (st.status === 'SAVEPOINT_SET') {
                  badgeVariant = 'APPROVED';
                  iconColor = 'bg-blue-500 text-white';
                }

                return (
                  <div key={st.step_number} className="relative group">
                    {/* Timeline Dot */}
                    <div className={`absolute -left-[27px] top-1.5 w-4 h-4 rounded-full border-2 border-slate-950 flex items-center justify-center ${iconColor}`}>
                      <span className="text-[9px] font-bold">{st.step_number}</span>
                    </div>

                    {/* Step Card */}
                    <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 transition-colors space-y-2">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <span className="text-xs font-bold font-mono text-white flex items-center gap-2">
                          {st.operation_name}
                        </span>
                        <Badge variant={st.status} />
                      </div>

                      <div className="p-2 rounded bg-slate-950 border border-slate-800/80 font-mono text-xs text-amber-300">
                        {st.sql}
                      </div>

                      <p className="text-xs text-slate-400">{st.details}</p>

                      {st.database_state_snapshot && (
                        <div className="text-[10px] font-mono text-slate-500 pt-1 border-t border-slate-800/60 flex items-center gap-2">
                          <span>SNAPSHOT:</span>
                          <span className="text-slate-400">{JSON.stringify(st.database_state_snapshot)}</span>
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
        <div className="glass-panel p-12 text-center rounded-2xl border border-slate-800 text-slate-400 text-xs">
          Select a transaction scenario above and click "Run Real Scenario" to observe live InnoDB ACID behavior.
        </div>
      )}
    </div>
  );
};

export default TransactionSimulatorPage;
