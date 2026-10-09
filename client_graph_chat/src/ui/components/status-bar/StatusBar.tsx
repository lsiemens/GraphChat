import { useClient } from  "@/ui/hooks/useClient"
import { StatusMessage } from "./StatusMessage"
import styles from "./StatusBar.module.css"

export function StatusBar() {
  const { state } = useClient();

  const latestStatus = state.status.at(-1);
  let summary: string;

  if (latestStatus === undefined) {
    return null;
  }

  if (state.status.length === 1) {
    summary = `Error : ${latestStatus.message}`
  } else {
    summary = `Errors (${state.status.length}): ${latestStatus.message}, ...`
  }

  return (
    <div className={styles["status-bar"]}>
      <span>{summary}</span>
      <div className={styles["status-tooltip"]}>
        {state.status.map((status, index) => (
          <StatusMessage key={index} status={status} />
        ))}
      </div>
    </div>
  );
}
