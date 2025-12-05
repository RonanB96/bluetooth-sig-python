src.bluetooth_sig.utils.profiling
=================================

.. py:module:: src.bluetooth_sig.utils.profiling

.. autoapi-nested-parse::

   Profiling and performance measurement utilities for Bluetooth SIG library.



Attributes
----------

.. autoapisummary::

   src.bluetooth_sig.utils.profiling.T


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.utils.profiling.TimingResult
   src.bluetooth_sig.utils.profiling.ProfilingSession


Functions
---------

.. autoapisummary::

   src.bluetooth_sig.utils.profiling.timer
   src.bluetooth_sig.utils.profiling.benchmark_function
   src.bluetooth_sig.utils.profiling.compare_implementations
   src.bluetooth_sig.utils.profiling.format_comparison


Module Contents
---------------

.. py:data:: T

.. py:class:: TimingResult

   Bases: :py:obj:`msgspec.Struct`


   Result of a timing measurement.


   .. py:attribute:: operation
      :type:  str


   .. py:attribute:: iterations
      :type:  int


   .. py:attribute:: total_time
      :type:  float


   .. py:attribute:: avg_time
      :type:  float


   .. py:attribute:: min_time
      :type:  float


   .. py:attribute:: max_time
      :type:  float


   .. py:attribute:: per_second
      :type:  float


.. py:class:: ProfilingSession

   Bases: :py:obj:`msgspec.Struct`


   Track multiple profiling results in a session.


   .. py:attribute:: name
      :type:  str


   .. py:attribute:: results
      :type:  list[TimingResult]


   .. py:method:: add_result(result: TimingResult) -> None

      Add a timing result to the session.



.. py:function:: timer(_operation: str = 'operation') -> collections.abc.Generator[dict[str, float], None, None]

   Context manager for timing a single operation.

   :param _operation: Name of the operation being timed (currently unused, reserved for future use)

   :Yields: Dictionary that will contain 'elapsed' key with timing result

   .. admonition:: Example

      >>> with timer("parse") as t:
      ...     parse_characteristic(data)
      >>> print(f"Elapsed: {t['elapsed']:.4f}s")


.. py:function:: benchmark_function(func: Callable[[], T], iterations: int = 1000, operation: str = 'function') -> TimingResult

   Benchmark a function by running it multiple times.

   :param func: Function to benchmark (should take no arguments)
   :param iterations: Number of times to run the function
   :param operation: Name of the operation for reporting

   :returns: TimingResult with detailed performance metrics

   .. admonition:: Example

      >>> result = benchmark_function(
      ...     lambda: translator.parse_characteristic("2A19", b"\\x64"),
      ...     iterations=10000,
      ...     operation="Battery Level parsing",
      ... )
      >>> print(result)

   .. note::

      Uses time.perf_counter() for high-resolution timing. The function
      includes a warmup run to avoid JIT compilation overhead in the
      measurements. Individual timings are collected to compute min/max
      statistics.


.. py:function:: compare_implementations(implementations: dict[str, Callable[[], Any]], iterations: int = 1000) -> dict[str, TimingResult]

   Compare performance of multiple implementations.

   :param implementations: Dict mapping implementation name to callable
   :param iterations: Number of times to run each implementation

   :returns: Dictionary mapping implementation names to their TimingResults

   .. admonition:: Example

      >>> results = compare_implementations(
      ...     {
      ...         "manual": lambda: manual_parse(data),
      ...         "sig_lib": lambda: translator.parse_characteristic("2A19", data),
      ...     },
      ...     iterations=10000,
      ... )
      >>> for name, result in results.items():
      ...     print(f"{name}: {result.avg_time * 1000:.4f}ms")


.. py:function:: format_comparison(results: dict[str, TimingResult], baseline: str | None = None) -> str

   Format comparison results as a human-readable table.

   :param results: Dictionary of timing results
   :param baseline: Optional name of baseline implementation for comparison

   :returns: Formatted string with comparison table


