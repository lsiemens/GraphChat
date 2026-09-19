import { Group, Panel, Separator } from "react-resizable-panels";
import styles from "./SplitView.module.css";

type Props = {
  left: React.ReactNode;
  right: React.ReactNode;
};

export function SplitView({ left, right }: Props) {
  return (
    <Group className={styles.group} orentation="horizontal">
      <Panel defaultSize="40%" minSize="20%" collapsible collapsedSize="0%">
        {left}
      </Panel>
      <Separator className={styles.separator} />
      <Panel minSize="20%">
        {right}
      </Panel>
    </Group>
  )
}
