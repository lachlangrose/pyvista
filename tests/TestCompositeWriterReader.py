from pathlib import Path

from vtkmodules import vtkCommonDataModel as dm, vtkImagingCore as ic, vtkIOLegacy as il
from vtkmodules.test import Testing
from vtkmodules.util.misc import vtkGetTempDir

import pyvista as pv


class TestCompositeWriterReader(Testing.vtkTest):

    def test(self):
        p = pv.PartitionedDataSet()

        s = ic.vtkRTAnalyticSource()
        s.SetWholeExtent(0, 10, 0, 10, 0, 5)
        s.Update()

        p1 = dm.vtkImageData()
        p1.ShallowCopy(s.GetOutput())

        s.SetWholeExtent(0, 10, 0, 10, 5, 10)
        s.Update()

        p2 = dm.vtkImageData()
        p2.ShallowCopy(s.GetOutput())

        p.SetPartition(0, p1)
        p.SetPartition(1, p2)

        p2 = pv.PartitionedDataSet()
        p2.ShallowCopy(p)

        c = dm.vtkPartitionedDataSetCollection()
        c.SetPartitionedDataSet(0, p)
        c.SetPartitionedDataSet(1, p2)

        tmpdir = vtkGetTempDir()
        fname = tmpdir + "/testcompowriread.vtk"
        w = il.vtkCompositeDataWriter()
        w.SetInputData(c)
        w.SetFileName(fname)
        w.Write()

        r = il.vtkCompositeDataReader()
        r.SetFileName(fname)
        r.Update()
        o = r.GetOutputDataObject(0)

        assert o.IsA("vtkPartitionedDataSetCollection")
        number_of_datasets = o.GetNumberOfPartitionedDataSets()
        assert number_of_datasets == 2

        for i in range(number_of_datasets):
            p = o.GetPartitionedDataSet(i)
            p2 = c.GetPartitionedDataSet(i)
            assert p.IsA("vtkPartitionedDataSet")
            assert p.GetNumberOfPartitions() == 2
            assert p.GetPartition(0).GetNumberOfCells() == p.GetPartition(0).GetNumberOfCells()
        del r
        import gc

        gc.collect()
        Path.unlink(fname)


if __name__ == "__main__":
    Testing.main([(TestCompositeWriterReader, 'test')])