export type ViewName = string & { readonly __brand: "ViewName" }

export function toViewName(input: string): ViewName {
  const viewNamePattern = /^[ -~]+$/;
  if (!viewNamePattern.test(input)) {
    throw new Error("ViewName must contain only printable characters");
  }

  return input as ViewName;
}

export function fromViewName(model: ViewName): string {
  return model;
}

export function toViewNames(inputs: readonly string[]): ViewName[] {
  return inputs.map((input) => {
    return toViewName(input);
  });
}
