const FINGERPRINT_LENGTH = 10;

export type NodeID = string & { readonly __brand: "NodeID" }

export function toNodeID(input: string): NodeID {
  const nodeIDPattern = /^[0-9a-f]+$/;
  if (typeof input !== "string") {
    throw new Error("NodeID must be a string");
  }
  if (input.length !== 64) {
    throw new Error("NodeID must be 64 characters in length");
  }
  if (!nodeIDPattern.test(input)) {
    throw new Error("NodeID must contain only hexadecimal characters [0-9a-f]");
  }

  return input as NodeID;
}

export function fromNodeID(nodeID: NodeID): string {
  return nodeID;
}

export function toNodeIDs(inputs: readonly string[]): NodeID[] {
  return inputs.map((input) => {
    return toNodeID(input);
  });
}

export function fromNodeIDs(nodeIDs: NodeID[]): string[] {
  return nodeIDs.map((nodeID) => {
    return fromNodeID(nodeID);
  });
}

export function nodeIDToString(nodeID: NodeID): string {
  return `NodeID(${nodeID.slice(0, FINGERPRINT_LENGTH)})`;
}
