import AnswerRow from "./AnswerRow";

export default function CompanyCard({ report }) {
  const answers = Object.entries(report.questions);

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="bg-gray-600 px-6 py-4">
        <h2 className="text-white font-semibold text-lg">{report.company}</h2>
      </div>

      <div className="px-6 py-5 border-b border-gray-100">
        <p className="text-xs font-semibold uppercase tracking-widest text-gray-400 mb-2">Summary</p>
        <p className="text-gray-700 text-sm leading-relaxed">{report.summary}</p>
      </div>

      <div className="px-6 py-5">
        <p className="text-xs font-semibold uppercase tracking-widest text-gray-400 mb-4">Questions</p>
        <div className="space-y-4">
          {answers.map(([question, answer]) => (
            <AnswerRow key={question} question={question} answer={answer} />
          ))}
        </div>
      </div>
    </div>
  );
}
