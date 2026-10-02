export type ModelName = string & { readonly __brand: "ModelName" }

export function toModelName(input: string): ModelName {
  const nodeIDPattern = /^[ -~]+$/;
  if (!nodeIDPattern.test(input)) {
    throw new Error("ModelName must contain only printable characters");
  }

  return input as ModelName;
}

export function fromModelName(model: ModelName): string {
  return model;
}

export function toModelNames(inputs: readonly string[]): ModelName[] {
  return inputs.map((input) => {
    return toModelName(input);
  });
}
