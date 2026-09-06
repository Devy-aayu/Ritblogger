import GitHubSetup from "../../components/github/GitHubSetup";

export default function SettingsPage() {
  return (
    <main className="settings-page">
      <div className="page-header">
        <div className="page-label">System</div>
        <h1>Settings</h1>
        <p>
          Configure the services used by the Ritnav Blog Engine.
        </p>
      </div>

      <GitHubSetup />
    </main>
  );
}