import type { Status } from "@/types"
import styles from "./StatusMessage.module.css"

interface Props {
  status: Status;
}

export function StatusMessage({ status }: Props) {
  return (
    <div className={styles["status"]}>
      <div className={styles["message"]}>
        {status.message}
      </div>
      {status.details && (
        <div className={styles["details"]}>
          Details: {status.details}
        </div>
      )}
    </div>
  );
}
