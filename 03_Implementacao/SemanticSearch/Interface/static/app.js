const { useState, useEffect } = React;

const QueryForm = ({ onSearch, isStartupDone, selectedBuckets }) => {
    const [query, setQuery] = useState('');
    const [k, setK] = useState(3);
    const [error, setError] = useState(null);
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!isStartupDone) {
            setError('Cannot search until all buckets are processed');
            return;
        }
        if (!query.trim()) {
            setError('Query cannot be empty');
            return;
        }
        if (k < 1) {
            setError('Number of results must be at least 1');
            return;
        }
        setError(null);
        setIsLoading(true);
        try {
            const response = await axios.post('/query', {
                query,
                k,
                buckets: selectedBuckets, // Only selected buckets!
            });
            onSearch(response.data.results);
        } catch (err) {
            setError(err.response?.data?.error || 'Failed to process query');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4">Semantic Search</h2>
            {!isStartupDone && (
                <div className="bg-yellow-100 text-yellow-700 p-4 rounded-lg mb-4 text-center font-medium">
                    Waiting for all buckets to process documents...
                </div>
            )}
            {error && (
                <div className="bg-red-100 text-red-700 p-3 rounded mb-4">
                    {error}
                </div>
            )}
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label htmlFor="query" className="block text-sm font-medium text-gray-700">
                        Search Query
                    </label>
                    <input
                        type="text"
                        id="query"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        disabled={!isStartupDone}
                        className={`mt-1 w-full p-2 border rounded-md focus:ring-indigo-500 focus:border-indigo-500 ${
                            !isStartupDone ? 'bg-gray-200 cursor-not-allowed' : ''
                        }`}
                        placeholder="Enter your search query"
                    />
                </div>
                <div>
                    <label htmlFor="k" className="block text-sm font-medium text-gray-700">
                        Number of Results (k)
                    </label>
                    <input
                        type="number"
                        id="k"
                        value={k}
                        onChange={(e) => setK(parseInt(e.target.value) || 1)}
                        disabled={!isStartupDone}
                        min="1"
                        className={`mt-1 w-full p-2 border rounded-md focus:ring-indigo-500 focus:border-indigo-500 ${
                            !isStartupDone ? 'bg-gray-200 cursor-not-allowed' : ''
                        }`}
                    />
                </div>
                <button type="submit" disabled={!isStartupDone || selectedBuckets.length === 0}>
                    Search
                </button>
            </form>
        </div>
    );
};

const ResultsDisplay = ({ results }) => {
    const [expandedChunks, setExpandedChunks] = useState({});

    const toggleChunk = (index) => {
        setExpandedChunks((prev) => ({
            ...prev,
            [index]: !prev[index],
        }));
    };

    const safeResults = Array.isArray(results) ? results : [];

    if (safeResults.length === 0) {
        return <p className="text-gray-600 mt-4">No results found. Try a different query.</p>;
    }

    const resultsByBucket = safeResults.reduce((acc, result) => {
        const bucketName = result.bucket_name || 'Unknown Bucket';
        if (!acc[bucketName]) {
            acc[bucketName] = [];
        }
        acc[bucketName].push(result);
        return acc;
    }, {});

    return (
        <div className="mt-6">
            <h3 className="text-lg font-semibold mb-4">Search Results</h3>
            {Object.entries(resultsByBucket).map(([bucketName, bucketResults]) => (
                <div key={bucketName} className="mb-6">
                    <h4 className="text-md font-medium text-gray-800 mb-3">Results from {bucketName}</h4>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                        {bucketResults.map((result, index) => (
                            <div key={index} className="bg-white p-4 rounded-lg shadow-md">
                                <div className="flex justify-between items-center mb-2">
                                    <div>
                                        <p className="font-medium">{result.name}</p>
                                        <p className="text-sm text-gray-600">
                                            Similarity: {(result.similarity * 100).toFixed(2)}%
                                        </p>
                                    </div>
                                    <a
                                        href={`/download/${bucketName}/${encodeURIComponent(result.location)}`}
                                        download
                                        className="py-2 px-4 bg-green-600 text-white rounded-md hover:bg-green-700"
                                    >
                                        Download
                                    </a>
                                </div>
                                <div>
                                    <p className="text-sm text-gray-600">
                                        Matching Chunk:{' '}
                                        {result.chunk ? (
                                            expandedChunks[`${bucketName}-${index}`] ? (
                                                result.chunk
                                            ) : (
                                                result.chunk.length > 100
                                                    ? `${result.chunk.substring(0, 100)}...`
                                                    : result.chunk
                                            )
                                        ) : (
                                            'No chunk available'
                                        )}
                                    </p>
                                    {result.chunk && result.chunk.length > 100 && (
                                        <button
                                            onClick={() => toggleChunk(`${bucketName}-${index}`)}
                                            className="mt-2 text-indigo-600 hover:text-indigo-800 text-sm"
                                        >
                                            {expandedChunks[`${bucketName}-${index}`] ? 'See Less' : 'See More'}
                                        </button>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            ))}
        </div>
    );
};

const RegisteredBuckets = ({ buckets }) => {
    if (!buckets || buckets.length === 0) {
        return <p className="text-gray-600 mt-4">No buckets registered.</p>;
    }

    return (
        <div className="mt-6">
            <h3 className="text-lg font-semibold mb-4">Registered Buckets</h3>
            <div className="grid grid-cols-1 sm:grid-cols-[repeat(auto-fit,minmax(220px,1fr))] gap-4 max-w-5xl mx-auto">
                {buckets.map((bucket, index) => (
                    <div
                        key={index}
                        className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow"
                    >
                        <p className="font-medium text-gray-800">{bucket.name}</p>
                        <p className="text-sm text-gray-500 mt-1">URL: {bucket.url}</p>
                    </div>
                ))}
            </div>
        </div>
    );
};

const App = () => {
    const [results, setResults] = useState([]);
    const [buckets, setBuckets] = useState([]);
    const [selectedBuckets, setSelectedBuckets] = useState([]);
    const [isStartupDone, setIsStartupDone] = useState(false);
    const [pollAttempts, setPollAttempts] = useState(0);

    useEffect(() => {
        const maxPollAttempts = 90; // 15 minutes at 10s intervals
        const basePollInterval = 10000; // 10 seconds

        const pollStartup = async (attempt = 0) => {
            if (pollAttempts >= maxPollAttempts) {
                console.error('Startup polling timed out after 15 minutes');
                setIsStartupDone(true);
                return;
            }
            try {
                const response = await axios.get('/buckets');
                setIsStartupDone(response.data.all_ready);
                if (!response.data.all_ready) {
                    console.log('Buckets still processing:', response.data.message);
                    setPollAttempts((prev) => prev + 1);
                    const backoff = Math.min(basePollInterval * Math.pow(2, attempt), 40000);
                    setTimeout(() => pollStartup(attempt + 1), backoff);
                }
            } catch (err) {
                console.error(`Poll attempt ${pollAttempts + 1} failed:`, err.message);
                setPollAttempts((prev) => prev + 1);
                const backoff = Math.min(basePollInterval * Math.pow(2, attempt), 40000);
                setTimeout(() => pollStartup(attempt + 1), backoff);
            }
        };

        axios.get('/buckets')
            .then((response) => {
                console.log('Fetched buckets:', response.data.buckets);
                setBuckets(response.data.buckets);
                setSelectedBuckets((response.data.buckets || []).map((b) => b.name)); // default: all selected
                if (response.data.buckets.length > 0) {
                    pollStartup();
                } else {
                    console.log('No buckets registered, skipping startup check');
                    setIsStartupDone(true);
                }
            })
            .catch((err) => {
                console.error('Failed to fetch buckets:', err);
                setIsStartupDone(true);
            });
    }, [pollAttempts]);

    const handleBucketChange = (bucketName) => {
        setSelectedBuckets((prev) =>
            prev.includes(bucketName)
                ? prev.filter((name) => name !== bucketName)
                : [...prev, bucketName]
        );
    };

    const handleSelectAll = () => {
        if (selectedBuckets.length === buckets.length) {
            setSelectedBuckets([]);
        } else {
            setSelectedBuckets(buckets.map((b) => b.name));
        }
    };

    return (
        <div className="max-w-5xl mx-auto p-6">
            <h1 className="text-3xl font-bold text-center mb-8">Semantic Search Interface</h1>
            <RegisteredBuckets buckets={buckets} />
            <div className="mb-4">
                <div className="flex items-center mb-2">
                    <button
                        type="button"
                        className="mr-2 px-2 py-1 bg-blue-500 text-white rounded"
                        onClick={handleSelectAll}
                    >
                        {selectedBuckets.length === buckets.length ? 'Unselect All' : 'Select All'}
                    </button>
                    <span className="text-gray-700 font-semibold">Buckets:</span>
                </div>
                <div className="max-h-48 overflow-y-auto border rounded p-2 bg-white shadow-sm" style={{minWidth: 220}}>
                    {buckets.map((bucket) => (
                        <label key={bucket.name} className="flex items-center mb-1 cursor-pointer">
                            <input
                                type="checkbox"
                                checked={selectedBuckets.includes(bucket.name)}
                                onChange={() => handleBucketChange(bucket.name)}
                                className="mr-2"
                            />
                            <span className="truncate" title={bucket.name}>{bucket.name}</span>
                        </label>
                    ))}
                </div>
            </div>
            <QueryForm onSearch={setResults} isStartupDone={isStartupDone} selectedBuckets={selectedBuckets} />
            {!isStartupDone && (
                <div className="text-center text-yellow-700 bg-yellow-100 border border-yellow-300 rounded p-3 mt-4">
                    Please wait: All buckets are being processed. Search will be enabled when ready.
                </div>
            )}
            {isStartupDone && <ResultsDisplay results={results} />}
        </div>
    );
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);