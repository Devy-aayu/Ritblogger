import AISetup from "../../components/ai/AISetup";
import GitHubSetup from "../../components/github/GitHubSetup";


export default function SettingsPage() {
  return (
    <>
      <header className="topbar">
        <div>
          <div className="page-label">
            System
          </div>

          <h1>
            Settings
          </h1>

          <p className="dashboard-description">
            Configure the services used by the
            Ritnav Blog Engine.
          </p>
        </div>
      </header>


      <div className="settings-stack">
        <GitHubSetup />

        <AISetup />
      </div>
    </>
  );
}