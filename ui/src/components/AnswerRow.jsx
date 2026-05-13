const confidenceColors = {
  high:   "text-gray-700",
  medium: "text-gray-500",
  low:    "text-gray-400",
};

export default function AnswerRow({ question, answer }) {
  const isFound = answer.status === "found";

  return (
    <div className="border border-gray-100 rounded-xl p-4">
      <p className="text-sm font-medium text-gray-800 mb-2">{question}</p>

      {isFound ? (
        <div className="space-y-2">
          <p className="text-sm text-gray-600 leading-relaxed">{answer.answer}</p>
          <hr className="border-gray-100" />
          <div className="flex flex-wrap items-center gap-2 pt-1">
            <span className={`text-xs font-semibold ${confidenceColors[answer.confidence]}`}>
              {answer.confidence} confidence
            </span>
            {answer.source && (
              <span className="text-xs text-gray-400">
                p.{answer.source.page} — <em>"{answer.source.quote}"</em>
              </span>
            )}
          </div>
        </div>
      ) : (
        <p className="text-sm text-gray-400 italic">Not found in report</p>
      )}
    </div>
  );
}
