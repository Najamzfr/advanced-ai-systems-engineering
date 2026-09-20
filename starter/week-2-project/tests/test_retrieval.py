import json, unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parents[1]))
import project
class RetrievalContract(unittest.TestCase):
    def setUp(self):
        self.rows=project.load_rows(True); self.row=self.rows[0]
    def test_all_methods_rank_same_corpus(self):
        ids={d['id'] for d in project.documents(self.row)}
        for method in project.METHODS:
            ranked,_=project.rank_documents(self.row,method)
            self.assertEqual(set(ranked),ids)
    def test_reranker_does_not_use_gold_label(self):
        row={'case_id':'fixed','question':'which method improves recall?', 'evidence_id':'doc-a', 'documents':[{'id':'doc-a','title':'A','section':'results','text':'method improves recall with a hybrid index'},{'id':'doc-b','title':'B','section':'intro','text':'the baseline has lower recall'}]}
        a=project.run_case(row,0); altered=dict(row); altered['evidence_id']='not-in-docs'; b=project.run_case(altered,0)
        self.assertEqual(a['methods']['hybrid_rerank']['top_k'],b['methods']['hybrid_rerank']['top_k'])
    def test_metrics_are_derived_and_six_methods_present(self):
        _,metrics=project.run(self.rows)
        self.assertEqual(set(metrics['method_rows']),set(project.METHODS)); self.assertEqual(set(metrics['required_metrics']),set(project.REQUIRED))
    def test_cited_answer_is_retrieved_evidence(self):
        result=project.run_case(self.row,0)
        cited={item['evidence_id'] for item in result['cited_answer']['citations']}
        self.assertTrue(cited)
        self.assertTrue(cited.issubset(set(result['methods']['hybrid_rerank']['top_k'])))
    def test_question_command_returns_citations(self):
        answer=project.answer_question(self.rows,'Which retrieval method uses lexical terms?')
        self.assertEqual(answer['answer']['mode'],'extractive')
        self.assertTrue(answer['answer']['citations'])
if __name__=='__main__': unittest.main()
