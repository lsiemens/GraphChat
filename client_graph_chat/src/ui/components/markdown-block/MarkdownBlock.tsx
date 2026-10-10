import Markdown from "react-markdown"
import remarkGfm from "remark-gfm"
import styles from "./MarkdownBlock.module.css"

interface Props {
  content: string;
};

export function MarkdownBlock({ content }: Props) {
  return (
    <div className={styles["markdown-block"]}>
      <Markdown remarkPlugins={[remarkGfm]}>
        {content}
      </Markdown>
    </div>
  );
}
