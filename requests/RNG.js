import * as Witnet from "witnet-requests"

const src = new Witnet.RandomSource()

const aggregator = new Witnet.Aggregator(
    {
        reducer: Witnet.Types.REDUCERS.mode,
        filters: [],
    }
)

const tally = new Witnet.Tally(
    {
        reducer: Witnet.Types.REDUCERS.concatenateAndHash,
        filters: [],
    }
)

const query = new Witnet.Request()
  .addSource(src)
  .setAggregator(aggregator)
  .setTally(tally)
  .setQuorum(8, 51)
  .setFees(10 ** 8, 10 ** 6)
  .setCollateral(10 * 10 ** 9)

export { query as default }

