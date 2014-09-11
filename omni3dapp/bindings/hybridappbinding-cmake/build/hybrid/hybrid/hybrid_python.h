

#ifndef SBK_HYBRID_PYTHON_H
#define SBK_HYBRID_PYTHON_H

//workaround to access protected functions
#define protected public

#include <sbkpython.h>
#include <conversions.h>
#include <sbkenum.h>
#include <basewrapper.h>
#include <bindingmanager.h>
#include <memory>

#include <pysidesignal.h>
// Module Includes
#include <pyside_qtcore_python.h>
#include <pyside_qtgui_python.h>

// Binded library includes
#include <MainWindow.h>
// Conversion Includes - Primitive Types
#include <QStringList>
#include <qabstractitemmodel.h>
#include <QString>
#include <signalmanager.h>
#include <typeresolver.h>
#include <QTextDocument>
#include <QtConcurrentFilter>

// Conversion Includes - Container Types
#include <QMap>
#include <QStack>
#include <QLinkedList>
#include <QVector>
#include <QSet>
#include <QPair>
#include <pysideconversions.h>
#include <QQueue>
#include <QList>
#include <QMultiMap>

// Type indices
#define SBK_MAINWINDOW_IDX                                           0
#define SBK_hybrid_IDX_COUNT                                         1

// This variable stores all Python types exported by this module.
extern PyTypeObject** SbkhybridTypes;

// This variable stores all type converters exported by this module.
extern SbkConverter** SbkhybridTypeConverters;

// Converter indices
#define SBK_HYBRID_QLIST_QACTIONPTR_IDX                              0 // QList<QAction * >
#define SBK_HYBRID_QLIST_QDOCKWIDGETPTR_IDX                          1 // QList<QDockWidget * >
#define SBK_HYBRID_QLIST_QVARIANT_IDX                                2 // QList<QVariant >
#define SBK_HYBRID_QLIST_QSTRING_IDX                                 3 // QList<QString >
#define SBK_HYBRID_QMAP_QSTRING_QVARIANT_IDX                         4 // QMap<QString, QVariant >
#define SBK_hybrid_CONVERTERS_IDX_COUNT                              5

// Macros for type check

namespace Shiboken
{

// PyType functions, to get the PyObjectType for a type T
template<> inline PyTypeObject* SbkType< ::MainWindow >() { return reinterpret_cast<PyTypeObject*>(SbkhybridTypes[SBK_MAINWINDOW_IDX]); }

} // namespace Shiboken

#endif // SBK_HYBRID_PYTHON_H

