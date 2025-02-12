from src import transformers as tf
import unittest as ut
import pandas as pd
import numpy as np

DATA_PATH = 'tests/samples/'
INPUT = 'input/'
OUTPUT = 'output/'
CSV_PRECISION = 10

def launcher():
    suites = []
    suites.append(ut.defaultTestLoader.loadTestsFromTestCase(ButterTransformerTest))
    suites.append(ut.defaultTestLoader.loadTestsFromTestCase(SavGolTransformerTest))
    suites.append(ut.defaultTestLoader.loadTestsFromTestCase(ConcatenateTransformerTest))
    suites.append(ut.defaultTestLoader.loadTestsFromTestCase(EachNormalizerTransformerTest))
    suites.append(ut.defaultTestLoader.loadTestsFromTestCase(NormalizerTransformerTest))
    suites.append(ut.defaultTestLoader.loadTestsFromTestCase(MoveTargetsTest))
    suites.append(ut.defaultTestLoader.loadTestsFromTestCase(VarianceThreshold))
    suites.append(ut.defaultTestLoader.loadTestsFromTestCase(PipelineTransformerTest))
    
    #TODO: Add more
    return suites

class TransformerTest(ut.TestCase):

    def __init__(self,output,*args,**kwargs):
        if 'input_' in kwargs:
            input_ = kwargs['input_']
            kwargs.pop('input_',None)            
        else:
            input_ = 'generic_input.csv'
        super(TransformerTest, self).__init__(*args,**kwargs)              
        
        self.input = pd.read_csv(DATA_PATH+INPUT+input_,index_col=0)
        self.output = pd.read_csv(DATA_PATH+OUTPUT+output,index_col=0)
        self.transformer = None

    def test_calculate_dataframe(self):
        output = self.transformer.fit_transform(self.input)

        compare = output.round(CSV_PRECISION)==self.output.round(CSV_PRECISION)

        self.assertFalse(False in compare.values)

    def test_calculate_series(self):    
        serie = self.input[self.input.columns[0]]    
        output = self.transformer.fit_transform(serie)

        compare = output.round(CSV_PRECISION)==self.output[self.output.columns[0]].round(CSV_PRECISION)
        self.assertFalse(False in compare.values)

    def test_bad_data(self):
        try:   
            output = self.transformer.fit_transform('String')
            self.fail()
        except AssertionError:
            pass


class ButterTransformerTest(TransformerTest):
     
    def __init__(self,*args,**kwargs):
        super(ButterTransformerTest, self).__init__('butter_output.csv',*args,**kwargs)
        N = 3
        Wn = 0.05
        self.transformer = tf.ButterTransformer(N,Wn)       

class SavGolTransformerTest(TransformerTest):
     
    def __init__(self,*args,**kwargs):
        super(SavGolTransformerTest, self).__init__('savgol_output.csv',*args,**kwargs)
        self.transformer = tf.SavgolTransformer(15)       

class ConcatenateTransformerTest(TransformerTest):
     
    def __init__(self,*args,**kwargs):
        super(ConcatenateTransformerTest, self).__init__('concatenate_output.csv',*args,**kwargs)
        
        N = 3
        Wn = 0.05
        butter = tf.ButterTransformer(N,Wn)
        savgol = tf.SavgolTransformer(15)       
        self.transformer = tf.ConcatenateTransformer(butter,savgol)

    def test_calculate_series(self):    
        serie = self.input[self.input.columns[0]]    
        output = self.transformer.fit_transform(serie)

        compare = output.round(CSV_PRECISION)==self.output[[self.output.columns[0],self.output.columns[len(self.input.columns)]]].round(CSV_PRECISION)
        self.assertFalse(False in compare.values)

class EachNormalizerTransformerTest(TransformerTest):

    def __init__(self,*args,**kwargs):
        super(EachNormalizerTransformerTest, self).__init__('each_normalizer_output.csv',input_ = 'random_input.csv',*args,**kwargs)

        self.transformer = tf.EachNormalizer()

class PipelineTransformerTest(TransformerTest):
    
    def __init__(self,*args,**kwargs):
        super(PipelineTransformerTest, self).__init__('pipeline_output.csv',*args,**kwargs)

        N = 3
        Wn = 0.05
        bt = tf.ButterTransformer(N,Wn)
        nt = tf.Normalizer()       
        self.transformer = tf.PipelineTransformer(bt,nt)

    def test_calculate_series(self):
        
        randomData = pd.Series(np.random.rand(1000),name='Random')
        
        try:
            self.transformer.fit_transform(randomData)
        except Exception as ex:
            self.fail()

class NormalizerTransformerTest(TransformerTest):

    def __init__(self,*args,**kwargs):
        super(NormalizerTransformerTest, self).__init__('normalizer_output.csv',input_ = 'random_input.csv',*args,**kwargs)

        self.transformer = tf.Normalizer()

    def test_another_max(self):
        transformer2 = tf.Normalizer(max_=100)
        output = transformer2.fit_transform(self.input)

        compare = output.round(CSV_PRECISION) == (self.output*100).round(CSV_PRECISION)
        self.assertFalse(False in compare.values)

    def test_calculate_series(self):
        serie = self.input[self.input.columns[0]]    
        output = self.transformer.fit_transform(serie)

        #La salida sería la correspondiente con el each_normalizer
        real_output = pd.read_csv(DATA_PATH+OUTPUT+'each_normalizer_output.csv',index_col=0)

        compare = output.round(CSV_PRECISION)==real_output[self.output.columns[0]].round(CSV_PRECISION)
        self.assertFalse(False in compare.values)

class VarianceThreshold(ut.TestCase):
    def __init__(self,*args,**kwargs):
        super(VarianceThreshold, self).__init__(*args,**kwargs)

        self.data = pd.read_csv(DATA_PATH+INPUT+'variance_threshold_input.csv',index_col=0)
    
    def test_variance0(self):
        
        vt = tf.VarianceThresholdPD().fit_transform(self.data)
        output = self.data[['Random','Thresh 0.5']]
        compare = vt == output
        self.assertFalse(False in compare)

    def test_variance05(self):
        
        vt = tf.VarianceThresholdPD(threshold=0.5).fit_transform(self.data)
        output = self.data[['Random']]
        compare = vt == output
        self.assertFalse(False in compare)

    def test_variance_no_features(self):
        try:
            vt = tf.VarianceThresholdPD(threshold=np.inf).fit_transform(self.data)
            self.fail()
        except ValueError:
            pass

class MoveTargetsTest(ut.TestCase):

    def __init__(self,*args,**kwargs):
        super(MoveTargetsTest, self).__init__(*args,**kwargs)

        self.input = pd.read_csv(DATA_PATH+INPUT+'move_targets_input.csv')
        self.output = pd.read_csv(DATA_PATH+OUTPUT+'move_targets_output.csv')
        self.window = 10

    def _generic_comparator(self,mode):
        output = tf.MoveTargetsTransformer(window=self.window,mode=mode).fit_transform(self.input)

        compare = output['target'] == self.output[mode]
        self.assertFalse(False in compare.values)

    def test_only_seizure(self):
        self._generic_comparator('only')

    def test_half_seizure(self):
        self._generic_comparator('half')

    def test_start_seizure(self):
        self._generic_comparator('start')

    def test_end_seizure(self):
        self._generic_comparator('end')

    def test_bad_target(self):
        try:
            output = tf.MoveTargetsTransformer(target_col='No Existo').fit_transform(self.input)
            self.fail()
        except KeyError:
            pass
    def test_target_not_boolean(self):
        try:
            output = tf.MoveTargetsTransformer(target_col='Unnamed: 0').fit_transform(self.input)
            self.fail()
        except AssertionError:
            pass

    

