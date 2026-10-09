import { Prompt, Node } from "@/types"
import { type NodeID, toNodeID, toNodeIDs, fromNodeIDs } from "@/types"
import { type ModelName, toModelName, toModelNames, fromModelName } from "@/types"
import { type ViewName, toViewNames } from "@/types"
import { ServerError } from "@/types"

/* API Interfaces */

interface PromptAPI {
  model: string;
  upstream: string[];
  context: string[];
  timestamp: string;
  content: string;
}

interface NodeAPI {
  id: string;
  upstream: string[];
  context: string[];
  request: string;
  reply: string;
  model: string;
  costUSD: number | null;
}

interface NodeIDsAPI {
  ids: string[];
}

interface ModelNamesAPI {
  models: string[];
}

interface ViewNamesAPI {
  viewNames: string[];
}

interface ViewUpstreamAPI {
  upstream: string[];
}

interface ViewContextAPI {
  context: string[];
}

interface ErrorAPI {
  type: string;
  message: string;
}


/* Base Type Validation */

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isNumber(value: unknown): value is number {
  return typeof value === "number";
}

function isString(value: unknown): value is string {
  return typeof value === "string";
}

function isArrayOf<T>(value: unknown, guard: (value: unknown) => value is T): value is T[] {
  return Array.isArray(value) && value.every(guard);
}

function isNullable<T>(value: unknown, guard: (value: unknown) => value is T): value is T | null {
  return guard(value) || (value == null);
}

function validate<T>(value: unknown, guard: (value: unknown) => value is T, name: string): T {
  if (!guard(value)) {
    throw new Error(`Input data did not match ${name}`);
  }

  return value;
}

/* Type Validation */
function isNodeAPI(value: unknown): value is NodeAPI {
  if (!isRecord(value)) return false;

  return (
    isString(value["id"]) &&
    isArrayOf(value["upstream"], isString) &&
    isArrayOf(value["context"], isString) &&
    isString(value["request"]) &&
    isString(value["reply"]) &&
    isString(value["model"]) &&
    isNullable(value["costUSD"], isNumber)
  );
}

function isNodeIDsAPI(value: unknown): value is NodeIDsAPI {
  if (!isRecord(value)) return false;

  return isArrayOf(value["ids"], isString);
}

function isModelNamesAPI(value: unknown): value is ModelNamesAPI {
  if (!isRecord(value)) return false;

  return isArrayOf(value["models"], isString);
}

function isViewNamesAPI(value: unknown): value is ViewNamesAPI {
  if (!isRecord(value)) return false;

  return isArrayOf(value["viewNames"], isString);
}

function isViewContextAPI(value: unknown): value is ViewContextAPI {
  if (!isRecord(value)) return false;

  return isArrayOf(value["context"], isString);
}

function isErrorAPI(value: unknown): value is ErrorAPI {
  if (!isRecord(value)) return false;

  return (
    isString(value["type"]) &&
    isString(value["message"])
  );
}

/* Type Convsion */

export function apiToNode(input: unknown): Node {
  const nodeAPI = validate(input, isNodeAPI, "NodeAPI");

  const data  = {
    id: toNodeID(nodeAPI.id),
    upstream: toNodeIDs(nodeAPI.upstream),
    context: toNodeIDs(nodeAPI.context),
    request: nodeAPI.request,
    reply: nodeAPI.reply,
    model: toModelName(nodeAPI.model),
    costUSD: nodeAPI.costUSD,
  };
  return new Node(data);
}

export function apiFromPrompt(prompt: Prompt): PromptAPI {
  const data = {
    model: fromModelName(prompt.model),
    upstream: fromNodeIDs(prompt.upstream),
    context: fromNodeIDs(prompt.context),
    timestamp: new Date().toISOString(),
    content: prompt.content,
  };

  return data;
}

export function apiToNodeIDs(input: unknown): NodeID[] {
  const nodeIDsAPI = validate(input, isNodeIDsAPI, "NodeIDsAPI");

  return toNodeIDs(nodeIDsAPI.ids);
}

export function apiToModelNames(input: unknown): ModelName[] {
  const modelNamesAPI = validate(input, isModelNamesAPI, "ModelNamesAPI");

  return toModelNames(modelNamesAPI.models);
}

export function apiToViewNames(input: unknown): ViewName[] {
  const viewNamesAPI = validate(input, isViewNamesAPI, "ViewNamesAPI");

  return toViewNames(viewNamesAPI.viewNames);
}

export function apiFromViewUpstream(viewUpstream: readonly NodeID[]): ViewUpstreamAPI {
  const data = { upstream: fromNodeIDs(viewUpstream) }

  return data;
}

export function apiToViewContext(input: unknown): NodeID[] {
  const viewContextAPI = validate(input, isViewContextAPI, "ViewContextAPI");

  return toNodeIDs(viewContextAPI.context);
}

export function apiToServerError(input: unknown): ServerError {
  const errorAPI = validate(input, isErrorAPI, "ErrorAPI");

  return new ServerError(errorAPI.type, errorAPI.message);
}
