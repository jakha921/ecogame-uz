import { useCallback, useEffect, useRef } from "react";
import { gameApi } from "@/api/game";
import type { ActionItem } from "@/api/types";
import { useGameStore } from "@/stores/gameStore";
import { SYNC_INTERVAL_MS } from "@/game/data/constants";

export function useGameSync(sessionId: number | null) {
  const actionBuffer = useRef<ActionItem[]>([]);
  const { setProgress } = useGameStore();

  const pushAction = useCallback((action: ActionItem) => {
    actionBuffer.current.push(action);
  }, []);

  const flushBuffer = useCallback(async () => {
    if (!sessionId || actionBuffer.current.length === 0) return;
    const actions = [...actionBuffer.current];
    actionBuffer.current = [];
    try {
      const { data: progress } = await gameApi.submitActions(sessionId, actions);
      setProgress(progress);
    } catch {
      // Re-queue on failure
      actionBuffer.current = [...actions, ...actionBuffer.current];
    }
  }, [sessionId, setProgress]);

  // Periodic sync
  useEffect(() => {
    if (!sessionId) return;
    const interval = setInterval(flushBuffer, SYNC_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [sessionId, flushBuffer]);

  // Flush on unmount
  useEffect(() => {
    return () => {
      flushBuffer();
    };
  }, [flushBuffer]);

  return { pushAction, flushBuffer };
}
