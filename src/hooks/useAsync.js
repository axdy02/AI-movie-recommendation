import { useCallback, useEffect, useRef, useState } from "react";

export function useAsync(asyncFn, _dependencies = [], { immediate = true } = {}) {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(immediate);
  const asyncFnRef = useRef(asyncFn);

  useEffect(() => {
    asyncFnRef.current = asyncFn;
  }, [asyncFn]);

  const run = useCallback(
    async (...args) => {
      setLoading(true);
      setError("");
      try {
        const result = await asyncFnRef.current(...args);
        setData(result);
        return result;
      } catch (err) {
        setError(err.message || "Something went wrong.");
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [],
  );

  useEffect(() => {
    if (immediate) {
      run().catch(() => {});
    }
  }, [immediate, run]);

  return { data, setData, error, setError, loading, run };
}
